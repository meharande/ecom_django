from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"

    def ready(self):
        import apps.products.signals  # noqa: F401 (import for signal registration)
        # NOTE: policy registration which writes to the DB is now handled by
        # the `manage_policies` management command or a data migration.
