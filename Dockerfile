# TastePilot API — optional Railway builder (Settings → Builder → Dockerfile)
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src ./src
COPY data ./data
COPY images ./images

ENV PYTHONPATH=src
ENV DATA_PATH=data/processed/restaurants.parquet

EXPOSE 8000
CMD uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
