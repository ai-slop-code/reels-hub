.PHONY: test lint test-container

test: lint
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src

test-container:
	@echo "test-container: not built yet (plan item 0.2, chore/container-image)"
