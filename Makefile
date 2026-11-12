.PHONY: test lint fixtures test-container

test: fixtures lint
	uv run pytest

fixtures:
	sh tests/fixtures/make_fixtures.sh

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src

test-container:
	scripts/container-test.sh
