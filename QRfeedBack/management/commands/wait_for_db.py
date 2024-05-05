from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = "Wait for database initialisalition"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except Exception:
                self.stdout.write(
                    "Database is unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write("Database is available!")
