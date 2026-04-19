# ecom_django (API-only ecommerce)

Quick commands for development and Docker usage.

### Run docker compose in detach mode

```bash
docker compose up -d
```

### Remove services

```bash
docker compose down
```

### Update and build image again

```bash
docker compose build
```

### Open shell in a container

```bash
docker ps -a
docker exec -it <container-id> /bin/sh
```

### Remove docker objects

```bash
docker image ls
docker image rm <image-id>

docker volume ls
docker volume rm <volume-id>

docker network ls
docker network rm <network-id>

docker inspect <container-id>
```

### Apps and their URLs (development)

 - Auth service URL: http://127.0.0.1:8000/
 - Inventory service URL: http://127.0.0.1:8001/api/products/
 - pgAdmin URL: http://127.0.0.1:8080/browser/ (username: meharande@gmail.com, pwd: Mehar@123)
 - Celery Flower Dashboard URL: http://localhost:5555/workers
 - Rabbitmq URL: http://localhost:15672/ (username: guest, pwd: guest)

## Production deployment

Follow these steps to deploy the API in production using Docker Compose.

1. Copy the example environment file and fill secrets:

```bash
cp .env.example .env
# edit .env and set secure values for SECRET_KEY and database passwords
```

2. Build and start services using the production compose file:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

3. To view logs or check health:

```bash
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml ps
```

4. Recommended production notes:

- Run behind a TLS-terminating reverse proxy (nginx, load balancer).
- Store secrets in a secret manager or environment variables (do not commit `.env`).
- Use a process manager and monitoring (Prometheus, Sentry) for observability.
- Scale `web` with multiple replicas and use a shared media store for uploaded files.

### Nginx integration

For TLS termination and proxying to the `web` service, see `deploy.md` which contains an example `nginx` config and a `docker-compose` snippet. The nginx config is placed at `docker/nginx/default.conf` in this repo.

API examples and docs

 - OpenAPI schema: `/api/schema/`
 - Swagger UI: `/api/docs/`
 - Example HTTP requests and a Postman collection are in the `docs/` folder (`docs/api_examples.md`, `docs/postman_collection.json`).

### run docker compose in ditatch mode

```cmd
    docker compose up -d
```
### remove services 

```cmd
    docker compose down
```
### Update and build image again 

```cmd
    docker compose build
```

### open shell in any conatiner

```cmd
    docker ps -a 
    docker exec -it <container-id> 
```

### remove docker objects

```cmd
    docker image ls
    docker image rm <image-id>

    docker volume ls
    docker volume rm <volue-id>

    docker network ls
    docker network rm <network-id>

    docker inspect <container-id>
```

### Apps and their URLs

 - Auth service URL: http://127.0.0.1:8000/
 - Inventory service URL: http://127.0.0.1:8001/api/products/
 - pgAdmin URL: http://127.0.0.1:8080/browser/ (username: meharande@gmail.com, pwd: Mehar@123)
 - Celery Flower Dashboard URL: http://localhost:5555/workers
 - Rabbitmq URL: http://localhost:15672/ (username: guest, pwd: guest)
