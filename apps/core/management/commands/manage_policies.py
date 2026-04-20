from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default Permission and Policy rows for all resources (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--defaults-only",
            action="store_true",
            help="Only create default ABAC policies defined in code (no full permission sweep)",
        )

    def handle(self, *args, **options):
        from apps.products import policies as products_policies
        from apps.users import policies as users_policies

        defaults_only = options.get("defaults_only", False)

        self.stdout.write("Registering permissions and policies...")
        try:
            result_products = products_policies.register_all(defaults_only=defaults_only)
            result_users = users_policies.register_all(defaults_only=defaults_only)
            total_result = {
                "permissions": result_products["permissions"] + result_users["permissions"],
                "policies": result_products["policies"] + result_users["policies"]
            }
            self.stdout.write(self.style.SUCCESS(f"Permissions/policies processed: {total_result}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Failed to register policies: {exc}"))
            raise
