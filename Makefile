.PHONY: install dev migrate upgrade seed test lint docker-up docker-down worker

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

seed:
	python scripts/seed.py

test:
	pytest tests/ -v --asyncio-mode=auto

lint:
	ruff check app/ tests/
	mypy app/

worker:
	celery -A app.workers.celery_app worker --loglevel=info

beat:
	celery -A app.workers.celery_app beat --loglevel=info

flower:
	celery -A app.workers.celery_app flower --port=5555

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

shell:
	python -c "import asyncio; from app.core.database import AsyncSessionLocal; print('DB ready')"

gen-secret:
	python -c "import secrets; print(secrets.token_hex(32))"
