import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """ DJango command to pause execution until database ia available """
    def handle(self, *args, **options):
        self.stdout.write("waiting for db....")
        db_Conn = None
        while not db_Conn:
            try:
                db_Conn = connections["default"]
            except OperationalError:
                self.stdout.write("database unavailable for 1 secone") 
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('database available'))

