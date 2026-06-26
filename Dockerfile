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

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8002

CMD ["./entrypoint.sh"]
