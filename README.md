# Wamato Backend API

Uganda's Trusted Property Marketplace — REST API built with FastAPI.

## Features

- **Authentication** — JWT access & refresh tokens, bcrypt password hashing
- **Properties** — CRUD, advanced filters, map pins, photo uploads, unlock system
- **Short-Stay / Holiday** — Airbnb-style bookings with availability checks
- **Reviews** — Ratings with auto-aggregation on property
- **Messaging** — REST + WebSocket real-time chat
- **Payments** — MTN Mobile Money & Airtel Money integration
- **Notifications** — In-app notification system
- **Search** — Full-text search + autocomplete suggestions
- **Admin** — User & property management endpoints
- **Background Tasks** — Celery workers with Redis broker
- **Docker** — One-command setup with docker-compose

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Server | Uvicorn + Gunicorn |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | python-jose (JWT) + passlib/bcrypt |
| Cache | Redis + fastapi-cache2 |
| Rate Limiting | slowapi |
| File Storage | Local (Pillow) or Cloudinary |
| Background Jobs | Celery + Celery Beat |
| Payments | MTN MoMo API + Airtel Money |
| Logging | structlog |
| Testing | pytest-asyncio + httpx |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app factory
│   ├── core/                 # Config, DB, security, Redis, logging
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── api/v1/               # Route handlers
│   ├── services/             # Business logic
│   └── workers/              # Celery tasks
├── alembic/                  # Database migrations
├── tests/                    # pytest test suite
├── scripts/seed.py           # Sample data seeder
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── requirements.txt
```

---

## Getting Started

### 1. Prerequisites

- Python 3.12+
- PostgreSQL 16
- Redis 7

### 2. Clone & install

```bash
git clone https://github.com/m-wasswa21/wamato-backend.git
cd wamato-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database, Redis, and payment credentials
```

Generate a secure secret key:
```bash
make gen-secret
```

### 4. Run migrations

```bash
make upgrade
```

### 5. Seed sample data

```bash
python scripts/seed.py
```

### 6. Start the server

```bash
make dev
```

API is now running at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

## Docker Setup (Recommended)

Starts API + PostgreSQL + Redis + Celery Worker + Flower in one command:

```bash
cp .env.example .env
make docker-up
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Flower (Celery) | http://localhost:5555 |

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Current user profile |
| POST | `/api/v1/auth/change-password` | Change password |

### Properties
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/properties` | List with filters |
| POST | `/api/v1/properties` | Create listing |
| GET | `/api/v1/properties/{id}` | Property detail |
| PATCH | `/api/v1/properties/{id}` | Update listing |
| DELETE | `/api/v1/properties/{id}` | Delete listing |
| GET | `/api/v1/properties/featured` | Featured listings |
| GET | `/api/v1/properties/map` | Map pins |
| POST | `/api/v1/properties/{id}/photos` | Upload photos |
| POST | `/api/v1/properties/{id}/unlock` | Unlock contact info |

### Bookings
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/bookings` | Create booking |
| GET | `/api/v1/bookings/my` | My bookings (guest) |
| GET | `/api/v1/bookings/incoming` | Incoming bookings (host) |
| POST | `/api/v1/bookings/{id}/cancel` | Cancel booking |

### Search
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/search?q=Kololo` | Full-text search |
| GET | `/api/v1/search/suggestions?q=K` | Autocomplete |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/payments/initiate` | Initiate MTN MoMo / Airtel |
| GET | `/api/v1/payments/my` | Payment history |
| POST | `/api/v1/payments/callback/mtn` | MTN webhook |
| POST | `/api/v1/payments/callback/airtel` | Airtel webhook |

---

## Payments (Uganda)

Supports **MTN Mobile Money** and **Airtel Money**.

Set your MTN MoMo credentials in `.env`:
```env
MTN_MOMO_URL=https://sandbox.momodeveloper.mtn.com
MTN_MOMO_PRIMARY_KEY=your_key
MTN_MOMO_API_USER=your_user
MTN_MOMO_API_KEY=your_api_key
MTN_MOMO_ENV=sandbox
```

Switch `MTN_MOMO_ENV=production` when going live.

### Listing Packages
| Package | Price |
|---|---|
| Basic | UGX 20,000 |
| Premium | UGX 50,000 |
| Featured | UGX 100,000 |

### Unlock Packages
| Package | Price |
|---|---|
| Single Property | UGX 5,000 |
| 5 Properties | UGX 20,000 |
| Weekly Pass | UGX 30,000 |
| Monthly Pass | UGX 100,000 |

---

## Running Tests

```bash
make test
```

Requires a test PostgreSQL database `wamato_test`.

---

## Celery Workers

```bash
# Start worker
make worker

# Start scheduler (Celery Beat)
make beat

# Monitor via Flower UI
make flower
```

---

## Makefile Commands

```bash
make dev          # Start dev server with hot reload
make upgrade      # Run database migrations
make migrate      # Generate new migration (msg="description")
make seed         # Seed sample data
make test         # Run test suite
make worker       # Start Celery worker
make docker-up    # Start all services with Docker
make docker-down  # Stop all Docker services
make gen-secret   # Generate a secure SECRET_KEY
```

---

## Environment Variables

See [.env.example](.env.example) for the full list of configuration options.

---

## License

MIT
