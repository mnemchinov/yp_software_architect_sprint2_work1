FROM --platform=linux/amd64 python:3.11-slim

RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]