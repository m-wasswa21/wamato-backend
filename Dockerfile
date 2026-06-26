FROM python:3.12-slim

WORKDIR /app

# System deps for asyncpg + Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libjpeg-dev libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/properties uploads/avatars

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
