# Day-to-day commands. Run from the repo root.
.PHONY: db api web test lint seed

db:            ## start Postgres
	docker compose up -d db

api:           ## run the Django dev server on :8000
	cd apps/api && .venv/bin/python manage.py runserver 8000

web:           ## run the Next.js dev server on :3000
	cd apps/web && npm run dev

test:          ## run the API test suite
	cd apps/api && .venv/bin/pytest

lint:          ## lint both apps
	cd apps/api && .venv/bin/ruff check . && .venv/bin/ruff format --check .
	cd apps/web && npm run lint && npx tsc --noEmit

seed:          ## load Cedar Hollow Zoo (works once M1 models exist)
	cd apps/api && .venv/bin/python manage.py loaddata fixtures/cedar_hollow_seed.json
