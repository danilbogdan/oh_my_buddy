COMPOSE_CMD = $(shell if docker compose version > /dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)
COMPOSE_MANAGE_CMD = $(COMPOSE_CMD) -f docker-compose.local.yml run --rm app python manage.py

up:
	$(COMPOSE_CMD) up

daemon:
	$(COMPOSE_CMD) up -d

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
