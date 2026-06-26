# Deployment Guide — backend.wamatoestatesmanagementuganda.online

## Server Setup

### 1. Upload project to server

```bash
git clone https://github.com/m-wasswa21/wamato-backend.git /var/www/wamato-backend
cd /var/www/wamato-backend
```

### 2. Configure environment

```bash
cp .env.example .env
nano .env
# Set DATABASE_URL, REDIS_URL, SECRET_KEY, MTN credentials, etc.
```

### 3. Enable Apache modules

```bash
sudo a2enmod proxy proxy_http proxy_wstunnel rewrite ssl headers
sudo systemctl restart apache2
```

### 4. Add Apache VirtualHost

```bash
sudo cp deploy/apache-wamato-backend.conf /etc/apache2/sites-available/backend.wamatoestatesmanagementuganda.online.conf
sudo a2ensite backend.wamatoestatesmanagementuganda.online
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### 5. Issue SSL certificate (Certbot)

```bash
sudo certbot --apache -d backend.wamatoestatesmanagementuganda.online
```

### 6. Start Docker containers

```bash
cd /var/www/wamato-backend
docker compose up -d --build
```

### 7. Verify

```bash
curl https://backend.wamatoestatesmanagementuganda.online/health
# Expected: {"status":"ok","version":"1.0.0"}
```

---

## Ports in Use

| App | Host Port | Container Port |
|-----|-----------|----------------|
| Other FastAPI app | 8001 | — |
| **Wamato API** | **8002** | **8002** |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| Flower (Celery) | 5555 | 5555 |

---

## Useful Commands

```bash
# View live logs
docker compose logs -f api

# Restart API only
docker compose restart api

# Run migrations manually
docker compose exec api alembic upgrade head

# Seed sample data
docker compose exec api python scripts/seed.py

# Stop everything
docker compose down
```

---

## DNS

Point the subdomain A record to your server IP:

```
backend.wamatoestatesmanagementuganda.online  A  <your-server-ip>
```

SSL auto-renews via Certbot cron.
