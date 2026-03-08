.PHONY: mcp-up mcp-down run-local lint test create-db reset-db update-db

mcp-up:
	docker compose up -d --build

mcp-down:
	docker compose down

run-local:
	uv run main.py

create-db:
	uv run python -m src.indexer create-db

reset-db:
	uv run python -m src.indexer reset-db

update-db:
	uv run python -m src.indexer update-db

lint:
	uv sync --extra dev
	uv run ruff check src

test:
	uv sync --extra dev
	uv run pytest tests/ -v
