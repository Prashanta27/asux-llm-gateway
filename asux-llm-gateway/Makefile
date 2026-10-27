.PHONY: install test lint format typecheck check run docker-up docker-down

install:
	pip install -e ".[dev]"

test:
	pytest tests/

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

check: lint typecheck test

run:
	python -m asux_llm_gateway.__main__

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
