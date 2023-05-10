import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv в модель Ingredient'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.DATA_FILES_PATH,
                                 'data/ingredients.csv')
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            objs = [
                Ingredient(
                    name=row[0],
                    measurement_unit=row[1]
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(objs)
