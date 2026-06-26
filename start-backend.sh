#!/bin/bash

docker rm -f wamato-backend 2>/dev/null

docker build -t wamato-backend .

docker run -d \
  --name wamato-backend \
  --network wamato-net \
  --restart unless-stopped \
  -p 8002:8002 \
  -v /var/run/postgresql:/var/run/postgresql \
  -v /var/www/wamato-backend/uploads:/app/uploads \
  -e APP_NAME="Wamato API" \
  -e DEBUG="false" \
  -e ENVIRONMENT="production" \
  -e DATABASE_URL="postgresql+asyncpg://wamato:WamatoUG2026x@/wamato_db?host=/var/run/postgresql" \
  -e REDIS_URL="redis://wamato-redis:6379/0" \
  -e CELERY_BROKER_URL="redis://wamato-redis:6379/1" \
  -e CELERY_RESULT_BACKEND="redis://wamato-redis:6379/2" \
  -e SECRET_KEY="wamato-uganda-super-secret-key-2026-prod" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  -e REFRESH_TOKEN_EXPIRE_DAYS="30" \
  -e ALLOWED_ORIGINS='["https://wamatoestatesmanagementuganda.online","https://backend.wamatoestatesmanagementuganda.online"]' \
  -e UPLOAD_DIR="/app/uploads" \
  -e MAX_FILE_SIZE_MB="10" \
  -e MTN_MOMO_URL="https://sandbox.momodeveloper.mtn.com" \
  -e MTN_MOMO_ENV="sandbox" \
  -e FIRST_ADMIN_EMAIL="admin@wamato.ug" \
  -e FIRST_ADMIN_PASSWORD="Admin@1234!" \
  wamato-backend
