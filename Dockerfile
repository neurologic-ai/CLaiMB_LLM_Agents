# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # ensure our in-repo modules importable: "import main_orchestrator..."
    PYTHONPATH=/app

WORKDIR /app

# minimal native build tools (for wheels), git for pip VCS installs
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential \
    && rm -rf /var/lib/apt/lists/*

# ----- deps first (better build caching)
COPY requirements-runtime.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# ----- app code
COPY . /app
COPY cloud_infra_inputs/Sample2 /app/cloud_infra_inputs/Sample2

# optional: run as non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# persist these if you bind-mount
VOLUME ["/app/bus", "/app/results", "/app/orchestrator_output"]

# FastAPI port
EXPOSE 8000

# DO NOT set OPENAI_API_KEY in the image to avoid secret-in-image warnings
# Pass it at runtime:  -e OPENAI_API_KEY=sk-...

# start server
CMD ["uvicorn", "main_orchestrator.app_main:app", "--host", "0.0.0.0", "--port", "8000"]