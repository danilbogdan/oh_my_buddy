COMPOSE_CMD = $(shell if docker compose version > /dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)
COMPOSE_MANAGE_CMD = $(COMPOSE_CMD) run --rm backend python manage.py
BRANCH_NAME := $(shell git rev-parse --abbrev-ref HEAD)
PREPRUSH_TEST_BRANCHES := dev-1 dev-2 preprod

up:
	$(COMPOSE_CMD) up

daemon:
	$(COMPOSE_CMD) up -d

start-chat:
	$(COMPOSE_MANAGE_CMD) start_conversation

migrate:
	$(COMPOSE_MANAGE_CMD) migrate

down:
	$(COMPOSE_CMD) down --remove-orphans

build:
	$(COMPOSE_CMD) build

pull:
	$(COMPOSE_CMD) pull

migrations:
	$(COMPOSE_MANAGE_CMD) makemigrations

migrations-merge:
	$(COMPOSE_MANAGE_CMD) makemigrations --merge

psql:
	$(COMPOSE_CMD) exec db psql -U agro

shell:
	$(COMPOSE_MANAGE_CMD) shell

shell-sql:
	$(COMPOSE_MANAGE_CMD) shell --print-sql

superuser:
	$(COMPOSE_MANAGE_CMD) createsuperuser
