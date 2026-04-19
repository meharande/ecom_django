COMPOSE_PROD=docker-compose.prod.yml

.PHONY: build-prod up-prod down-prod logs-prod migrate-prod collectstatic-prod shell-prod build-nginx

build-prod:
	@echo "Building production images..."
	docker compose -f $(COMPOSE_PROD) build --pull

up-prod:
	@echo "Starting production stack..."
	docker compose -f $(COMPOSE_PROD) up -d --remove-orphans

down-prod:
	@echo "Stopping production stack..."
	docker compose -f $(COMPOSE_PROD) down

logs-prod:
	@echo "Tailing logs for web..."
	docker compose -f $(COMPOSE_PROD) logs -f web

migrate-prod:
	@echo "Running migrations on web..."
	docker compose -f $(COMPOSE_PROD) exec web python manage.py migrate --noinput

collectstatic-prod:
	@echo "Collecting static files on web..."
	docker compose -f $(COMPOSE_PROD) exec web python manage.py collectstatic --noinput

shell-prod:
	@echo "Opening shell in web container..."
	docker compose -f $(COMPOSE_PROD) exec web /bin/sh

build-nginx:
	@echo "Building nginx image"
	docker compose -f $(COMPOSE_PROD) build nginx
