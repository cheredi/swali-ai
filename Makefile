.PHONY: help install backend frontend test lint format pre-commit run-backend run-frontend process-data collect-ai-ml experiments

help:
	@echo "Common commands:"
	@echo "  make install          - Install backend and frontend dependencies"
	@echo "  make test             - Run pytest"
	@echo "  make lint             - Run ruff checks"
	@echo "  make format           - Run ruff format"
	@echo "  make run-backend      - Start FastAPI backend"
	@echo "  make run-frontend     - Start Vite frontend"
	@echo "  make process-data     - Build vector data"
	@echo "  make collect-ai-ml    - Collect AI/ML dataset"
	@echo "  make experiments      - Run retrieval experiments"
	@echo "  make pre-commit       - Run pre-commit on all files"

install:
	poetry install --with dev
	cd frontend && npm install

test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

pre-commit:
	poetry run pre-commit run --all-files

run-backend:
	cd backend && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

process-data:
	poetry run python scripts/process_data.py

collect-ai-ml:
	poetry run python scripts/collect_ai_ml.py

experiments:
	poetry run python scripts/run_retrieval_experiments.py
