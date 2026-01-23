import uvicorn
import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

# Thread pool for blocking Kafka operations
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI(
   title="CinemaAbyss Events Service",
   description="Kafka Producer/Consumer для событий User/Payment/Movie",
   version="1.0.0"
)

PORT = int(os.getenv("PORT", "8082"))
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")

MOVIE_EVENTS_TOPIC = "movie-events"
USER_EVENTS_TOPIC = "user-events"
PAYMENT_EVENTS_TOPIC = "payment-events"


class MovieEvent(BaseModel):
   movie_id: int
   title: Optional[str] = None
   action: Optional[str] = None
   user_id: Optional[int] = None
   timestamp: Optional[str] = None


class UserEvent(BaseModel):
   user_id: int
   username: Optional[str] = None
   action: Optional[str] = None
   timestamp: Optional[str] = None


class PaymentEvent(BaseModel):
    payment_id: int
    user_id: int
    amount: float
    status: str
    method_type: str
    timestamp: str


_producer: Optional[Producer] = None


def _get_producer() -> Producer:
   global _producer
   if _producer is None:
       _producer = Producer({'bootstrap.servers': KAFKA_BROKERS, 'client.id': 'events-service-producer'})
   return _producer


def _delivery_callback(err, msg):
   if err:
       print(f"Ошибка доставки сообщения: {err}")
   else:
       print(f"Собщение доставлено в {msg.topic()}: {msg.value()}")


async def _consume_messages(topic: str, service_name: str):
   consumer = Consumer({
       'bootstrap.servers': KAFKA_BROKERS,
       'group.id': f'{topic}-consumer-group',
       'auto.offset.reset': 'earliest',
       'enable.auto.commit': True
   })
   consumer.subscribe([topic])
   print(f"[{service_name}] Начато потребление из {topic}")

   try:
       while True:
           await asyncio.get_event_loop().run_in_executor(executor, partial(_consume_single, consumer, topic, service_name))
   except asyncio.CancelledError:
       print(f"[{service_name}] Потребление остановлено")
   except KafkaException as e:
       print(f"Ошибка Kafka в {service_name}: {e}")
   finally:
       consumer.close()


def _consume_single(consumer: Consumer, topic: str, service_name: str):
   """Blocking consume call executed in thread pool."""
   msg = consumer.consume(timeout=1.0)
   if msg:
       for m in msg:
           if m.error():
               if m.error().code() != KafkaError._PARTITION_EOF:
                   print(f"Ошибка consumer: {m.error()}")
           else:
               print(f"[{service_name}] Получено: {m.value().decode('utf-8')}")


async def _publish_event(topic: str, event_data: dict) -> dict:
   loop = asyncio.get_event_loop()
   producer = _get_producer()
   producer.produce(topic, json.dumps(event_data).encode('utf-8'), callback=_delivery_callback)
   await loop.run_in_executor(executor, producer.flush)
   return {"status": "success", "event": event_data}


@app.on_event("startup")
async def startup_event():
   print("Starting up...")
   asyncio.create_task(_consume_messages(MOVIE_EVENTS_TOPIC, "MoviesService"))
   asyncio.create_task(_consume_messages(USER_EVENTS_TOPIC, "UsersService"))
   asyncio.create_task(_consume_messages(PAYMENT_EVENTS_TOPIC, "PaymentsService"))


@app.get("/api/events/health")
async def health_check():
   return {"status": True, "service": "events", "kafka_brokers": KAFKA_BROKERS}


@app.post("/api/events/movie", status_code=201)
async def create_movie_event(event: MovieEvent):
   event_data = {
       "event_id": str(uuid.uuid4()),
       "movie_id": event.movie_id,
       "title": event.title,
       "action": event.action,
       "user_id": event.user_id,
       "timestamp": datetime.utcnow().isoformat()
   }
   try:
       return await _publish_event(MOVIE_EVENTS_TOPIC, event_data)
   except KafkaException as e:
       raise HTTPException(status_code=50, detail=f"Ошибка Kafka: {e}")


@app.post("/api/events/user", status_code=201)
async def create_user_event(event: UserEvent):
   event_data = {
       "event_id": str(uuid.uuid4()),
       "user_id": event.user_id,
       "username": event.username,
       "action": event.action,
       "timestamp": datetime.utcnow().isoformat()
   }
   try:
       return await _publish_event(USER_EVENTS_TOPIC, event_data)
   except KafkaException as e:
       raise HTTPException(status_code=50, detail=f"Ошибка Kafka: {e}")


@app.post("/api/events/payment", status_code=201)
async def create_payment_event(event: PaymentEvent):
   event_data = {
       "event_id": str(uuid.uuid4()),
       "payment_id": event.payment_id,
       "user_id": event.user_id,
       "amount": event.amount,
       "status": event.status,
       "timestamp": datetime.utcnow().isoformat()
   }
   try:
       return await _publish_event(PAYMENT_EVENTS_TOPIC, event_data)
   except KafkaException as e:
       raise HTTPException(status_code=50, detail=f"Ошибка Kafka: {e}")


if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=PORT)