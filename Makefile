.PHONY: test lint test-container

test: lint
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src

test-container:
	scripts/container-test.sh
