import django
from django.conf import settings
from stockProject import settings as project_settings

settings.configure(default_settings=project_settings, DEBUG=True)
django.setup()

from stockApp.models import StockData, Currency, Country


def load_data():
    usa = Country(name="United Stated")
    usa.save()

    us_dollar = Currency(name="USD")
    us_dollar.save()


if __name__ == "__main__":
    load_data()
