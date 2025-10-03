from django.apps import AppConfig


class MentalHealthAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mental_health_app"

    def ready(self):
        # Place signal registrations here if needed
        from . import signals  # noqa: F401
