# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements-runtime.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . /app

# Persist bus/results outside container if you bind-mount
VOLUME ["/app/bus", "/app/results"]

# FastAPI port
EXPOSE 8000

# The app reads OPENAI_API_KEY from env (we pass it via .env / compose)
ENV OPENAI_API_KEY=""

# Start FastAPI (points to your file)
CMD ["uvicorn", "main_orchestrator.app_main:app", "--host", "0.0.0.0", "--port", "8000"]