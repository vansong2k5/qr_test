.PHONY: setup dev backend-install frontend-install backend-test frontend-test migrate seed lint

setup: backend-install frontend-install

backend-install:
cd backend && pip install -e . && pip install -e .[tests]

frontend-install:
cd frontend && npm install

dev:
docker compose -f deploy/docker-compose.yml up --build

backend-test:
cd backend && pytest

frontend-test:
cd frontend && npm run test

migrate:
docker compose -f deploy/docker-compose.yml exec api alembic upgrade head

seed:
docker compose -f deploy/docker-compose.yml exec api python -m app.utils.seed

lint:
cd backend && ruff check src
