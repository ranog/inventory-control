PYTHON_VERSION = 3.11.3

.DEFAULT_GOAL := run

init: install-deps

install-deps:
	@pip install --upgrade pip setuptools wheel
	@pip install --upgrade poetry
	@poetry install
	@pre-commit install
	@pre-commit run --all-files

poetry-export:
	@poetry export --with dev -vv --no-ansi --no-interaction --without-hashes --format requirements.txt --output requirements.txt

lock-deps:
	@poetry lock -vv --no-ansi --no-interaction

.PHONY: ruff
ruff:
	@poetry run ruff format .

.PHONY: ruff-check
ruff-check:
	@poetry run ruff check .

.PHONY: flake8
flake8:
	@poetry run flake8 .

.PHONY: blue
blue:
	@poetry run blue -v .

.PHONY: blue-check
blue-check:
	@poetry run blue -v --check .

.PHONY: format
format: ruff blue

.PHONY: lint
lint: ruff-check flake8 blue-check

run: init
	@poetry run env $(shell grep -v ^\# .env | xargs) uvicorn src.main:app --reload --port 8080

build-container:
	@docker build \
		--tag ranog:inventory-control \
		--build-arg GIT_HASH=$(shell git rev-parse HEAD) \
		-f Dockerfile \
		.

run-container: poetry-export build-container
	@docker run --rm -it \
		--name ranog_inventory-control \
		--env-file .env \
		--env PORT=8080 \
		--publish 8080:8080 \
		ranog:inventory-control

test-all: init
	@poetry run env $(shell grep -v ^\# .env | xargs) pytest

# Docker compose

export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker-compose build

up:
	docker-compose up -d app

down:
	docker-compose down

logs:
	docker-compose logs app | tail -100

test:
	pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')
