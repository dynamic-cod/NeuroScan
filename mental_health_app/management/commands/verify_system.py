from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connections
from django.utils.module_loading import import_string


class Command(BaseCommand):
    help = "Verify system components are healthy"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Checking database connection..."))
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("Database OK"))

        self.stdout.write(self.style.NOTICE("Checking cache backend..."))
        cache.set("healthcheck", "ok", 10)
        assert cache.get("healthcheck") == "ok"
        self.stdout.write(self.style.SUCCESS("Cache OK"))

        self.stdout.write(self.style.NOTICE("Checking Celery app import..."))
        celery_app = import_string("neuroscan.celery.app")
        assert celery_app.main == "neuroscan"
        self.stdout.write(self.style.SUCCESS("Celery OK"))

        self.stdout.write(self.style.SUCCESS("All systems operational."))
