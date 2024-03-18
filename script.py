import os
import django
from random import shuffle

os.environ["DJANGO_SETTINGS_MODULE"] = "stockProject.settings"
django.setup()

import requests
from stockApp.models import StockData, Currency, Country


def check_data():
    if not StockData.objects.exists():
        print("Loading initial data...")
        load_data()
    return 0


def load_data():
    api_url = "https://api.twelvedata.com/stocks?country=United States&exchange=NASDAQ&type=Common Stock&currency=USD"

    usa, created = Country.objects.get_or_create(name="United States")
    us_dollar, created = Currency.objects.get_or_create(name="USD")

    response = requests.get(api_url)
    stocks_json: list = response.json()["data"]
    shuffle(stocks_json)
    for stock_data in stocks_json[:40]:
        StockData.objects.get_or_create(
            symbol=stock_data.get("symbol"),
            name=stock_data.get("name"),
            exchange=stock_data.get("exchange"),
            type=StockData.StockType.COMMON_STOCK,
            currency=us_dollar,
            country=usa,
        )

    return 0


if __name__ == "__main__":
    print("Start loading script...")
    check_data()
    print("Stock data in database.")
