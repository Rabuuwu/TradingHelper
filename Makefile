.PHONY: install dev test lint format run worker scan self-check init-db

install:
	python -m pip install -e .

dev:
	python -m pip install -e '.[dev]'

test:
	pytest --cov=trading_helper --cov-report=term-missing --cov-fail-under=70

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

run:
	python -m trading_helper.main run

worker:
	python -m trading_helper.main worker

scan:
	python -m trading_helper.main scan-once

self-check:
	python -m trading_helper.main self-check

init-db:
	python -m trading_helper.main init-db
