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
        from apps.products import policies

        defaults_only = options.get("defaults_only", False)

        self.stdout.write("Registering permissions and policies...")
        try:
            result = policies.register_all(defaults_only=defaults_only)
            self.stdout.write(self.style.SUCCESS(f"Permissions/policies processed: {result}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Failed to register policies: {exc}"))
            raise
