# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install build dependencies that many Python libs need (gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency spec and install
COPY requirements.txt ./requirements.txt

# Copy application code (everything under backend/app)
COPY ./app ./app
COPY ./data ./data

# Expose project root to Python path
ENV PYTHONPATH=/app/app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip

# Start FastAPI with Uvicorn (auto‑reload for dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
