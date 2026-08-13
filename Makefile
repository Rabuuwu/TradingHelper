.PHONY: install dev test lint format run self-check init-db

install:
	python -m pip install -e .

dev:
	python -m pip install -e '.[dev]'

test:
	pytest --cov=trading_helper --cov-report=term-missing

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

run:
	python -m trading_helper.main api

self-check:
	python -m trading_helper.main self-check

init-db:
	python -m trading_helper.main init-db
