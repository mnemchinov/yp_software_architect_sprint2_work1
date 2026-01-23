import uvicorn
import os
import random
import logging

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

app = FastAPI(title="CinemaAbyss Proxy Service", version="1.0.0")

# Конфигурация
PORT = int(os.getenv("PORT", "8000"))
MONOLITH_URL = os.getenv("MONOLITH_URL", "http://monolith:8080")
MOVIES_SERVICE_URL = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
GRADUAL_MIGRATION = os.getenv("GRADUAL_MIGRATION", "true").lower() == "true"
MOVIES_MIGRATION_PERCENT = int(os.getenv("MOVIES_MIGRATION_PERCENT", "50"))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "proxy"}


@app.get("/api/movies")
async def get_movies():
    """Проксирование запросов к фильмам с поддержкой Strangler Fig."""
    should_migrate = GRADUAL_MIGRATION and random.randint(0, 100) < MOVIES_MIGRATION_PERCENT
    target_url = f"{MOVIES_SERVICE_URL}/api/movies" if should_migrate else f"{MONOLITH_URL}/api/movies"

    try:
        response = await httpx.AsyncClient().get(target_url, follow_redirects=False, timeout=10.0)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return []
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except httpx.RequestError:
        # Fallback на другой сервис
        fallback_url = MOVIES_SERVICE_URL if should_migrate else MONOLITH_URL
        try:
            fallback_response = await httpx.AsyncClient().get(
                f"{fallback_url}/api/movies", follow_redirects=False, timeout=10.0
            )
            return fallback_response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/{path:path}")
async def proxy_generic(path: str):
    """Общий прокси для остальных запросов."""
    try:
        response = await httpx.AsyncClient().get(
            f"{MONOLITH_URL}/api/{path}", follow_redirects=False, timeout=10.0
        )
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
