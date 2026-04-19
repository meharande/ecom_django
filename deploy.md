# Deployment & troubleshooting

This document contains quick steps and troubleshooting tips for deploying the API using `docker-compose.prod.yml`.

Basic deploy steps

1. Copy and edit environment file

```bash
cp .env.example .env
# Edit .env with secure values (SECRET_KEY, DB passwords, ALLOWED_HOSTS)
```

2. Build and start services

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

3. Check service status and logs

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
```

Common issues & fixes

- Database hostname resolution

  Symptom: `could not translate host name "db" to address` when containers try to connect.

  Fix: Ensure you used the same compose network (running with the prod compose file) or set `POSTGRES_HOST` in `.env` to a reachable host. When running locally with the prod compose file, the service name `db` is correct.

- Migrations failing at container start

  Symptom: errors during `manage.py migrate` in the container.

  Fix:
  - Confirm DB credentials in `.env` are correct.
  - Check `docker compose -f docker-compose.prod.yml logs db` for Postgres errors.
  - Run `docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput` to see full traceback.

- Static files missing / 404s

  Fix: Ensure `collectstatic` ran successfully (entrypoint runs it). Verify `STATIC_ROOT` in settings and that your reverse proxy serves that folder. Use a shared storage (S3) in multi-replica setups.

- Worker (Celery) can't connect to broker

  Symptom: Celery logs show connection refused to RabbitMQ or Redis.

  Fix: Check `CELERY_BROKER_URL` and `REDIS_URL` values. Ensure the broker service is healthy and reachable (`docker compose ps` and logs).

- Secrets leaked or committed

  Fix: Never commit `.env`. Use `.env.example` for required keys. For production, use a secret manager or environment variables set by your orchestrator.

Debugging tips

- Recreate containers to pick up env changes:

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

- Get a shell in the running `web` container to inspect runtime state:

```bash
docker compose -f docker-compose.prod.yml exec web /bin/sh
```

- Tail all logs for quick diagnosis:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

If you want, I can also add a simple `nginx` reverse-proxy config example and a `systemd` unit for running the compose stack on a VM.

## Nginx reverse-proxy example & TLS notes

Example `docker-compose` service snippet for nginx (put this in your production compose or run as a separate stack):

```yaml
  nginx:
    build:
      context: ./docker/nginx
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./static:/vol/static:ro      # optional: serve static files from nginx
      - /etc/letsencrypt:/etc/letsencrypt:ro  # mount certs created by certbot
    depends_on:
      - web
    restart: unless-stopped
```

Place the example nginx config at `docker/nginx/default.conf` (already included). It proxies requests to the `web` service on port 8000.

TLS options and Let's Encrypt notes:

- Recommended: terminate TLS at nginx and keep internal traffic over the Docker network unencrypted.
- Use Certbot (Let's Encrypt) to provision certificates. On a VM you can run Certbot on the host and mount `/etc/letsencrypt` into the nginx container.
- For automated certificate renewal with Docker Compose, consider a small companion container like `linuxserver/letsencrypt` or use `certbot` in a host cron job and reload nginx after renewal.
- If using a cloud provider or Kubernetes, prefer the provider's TLS load balancer or an Ingress controller with cert-manager.

Security best practices:
- Redirect HTTP to HTTPS and enable HSTS (configured in the provided `default.conf`).
- Keep private keys outside of your repository and use a secrets manager where possible.
- Limit `client_max_body_size` to a reasonable value for your API.

