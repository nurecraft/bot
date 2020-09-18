include .env

tail := 200
PYTHONPATH := $(shell pwd):${PYTHONPATH}

PROJECT := nurecraft_bot
LOCALES_DOMAIN := bot
LOCALES_DIR := locales
VERSION := 0.1
PIPENV_VERBOSITY := -1

# =================================================================================================
# Base
# =================================================================================================

default:help

help:
	@echo "NURECRAFT Telegram Bot"

# =================================================================================================
# Development
# =================================================================================================

isort:
	pipenv run isort --recursive .

black:
	pipenv run black .

flake8:
	pipenv run flake8 .

lint: isort black flake8

entrypoint:
	pipenv run bash ../docker-entrypoint.sh ${args}

alembic:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic ${args}

migrate:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic upgrade head

migration:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic revision --autogenerate -m "${message}"

downgrade:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic downgrade -1

beforeStart: docker-up-db migrate

app:
	pipenv run python -m app ${args}

start:
	$(MAKE) beforeStart
	$(MAKE) app args="run-polling"

# =================================================================================================
# Docker
# =================================================================================================

docker-config:
	docker-compose config

docker-ps:
	docker-compose ps

docker-build:
	docker-compose build

docker-up-db:
	docker-compose up -d redis postgres

docker-up:
	docker-compose up -d --remove-orphans

docker-stop:
	docker-compose stop

docker-down:
	docker-compose down

docker-destroy:
	docker-compose down -v --remove-orphans

docker-logs:
	docker-compose logs -f --tail=${tail} ${args}

# =================================================================================================
# Application in Docker
# =================================================================================================

app-create: docker-build docker-stop docker-up

app-logs:
	$(MAKE) docker-logs args="bot"

app-stop: docker-stop

app-down: docker-down

app-start: docker-stop docker-up

app-destroy: docker-destroy

app-rebuild:
	$(MAKE) docker-build
	$(MAKE) app-start
