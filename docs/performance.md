# Performance & Database Recommendations

This file lists practical improvements to make the API faster and more production-ready.

1) Database indexes

- Review slow queries (use `pg_stat_statements`, Django debug toolbar) and add targeted indexes.
- Suggested indexes (Postgres):
  - Index on `apps_products_product` for commonly filtered columns (e.g. `name`):
    ```sql
    CREATE INDEX CONCURRENTLY idx_products_name ON apps_products_product (name);
    ```
  - Partial index for active rows if many soft-deleted rows exist:
    ```sql
    CREATE INDEX CONCURRENTLY idx_products_active ON apps_products_product (id) WHERE deleted_at IS NULL AND is_active;
    ```
  - Index JSONField keys if you query them often (GIN index):
    ```sql
    CREATE INDEX CONCURRENTLY idx_sku_attributes ON apps_products_sku USING gin (attributes);
    ```

2) Use `select_related` / `prefetch_related`

- Ensure list/detail views use `select_related` for FK joins (e.g. `Product` -> `brand`, `subcategory`) and `prefetch_related` for reverse relations (`skus`, `images`) to avoid N+1 queries.
- Example:

```python
qs = Product.objects.select_related('brand', 'subcategory').prefetch_related('skus__images')
```

3) Caching

- Use Redis (already configured) to cache expensive query results or computed responses.
- For read-heavy endpoints, consider cache with short TTL and invalidate on writes.
- Use `django.core.cache` for low-level caching or `@cache_page` for view-level caching.

4) Pagination and throttling

- Pagination: use limit/offset or cursor pagination for large result sets (configured in settings).
- Throttling: basic anon/user throttles added in settings; tune rates to match expected traffic.

5) Rate-limiting & abuse protection

- For stricter rate-limiting, add a gateway (Cloudflare) or API gateway (Kong) in front of the app, or use more advanced DRF throttles backed by Redis.

6) Index maintenance & migrations

- Create indexes using `CREATE INDEX CONCURRENTLY ...` to avoid locks on large tables.
- Add index creation in Django migrations using `RunSQL` with `CONCURRENTLY` where appropriate (Postgres only).

7) Read replicas & connection pooling

- For high-read scale, configure read replicas and send read queries to replicas.
- Use a connection pooler (pgbouncer) to reduce DB connection overhead.

8) Monitoring & profiling

- Add Prometheus + Grafana for metrics and APM (Sentry, New Relic) for request traces.
- Use `EXPLAIN ANALYZE` for slow queries and optimize accordingly.

If you'd like, I can:
- Implement `select_related`/`prefetch_related` in product list/detail endpoints.
- Add example Django migrations to create recommended indexes.
- Add cache decorators to key views.
