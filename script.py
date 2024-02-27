import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "stockProject.settings"
django.setup()

import requests
from stockApp.models import StockData, Currency, Country


def load_data():
    api_url = "https://api.twelvedata.com/stocks?country=United States&exchange=NASDAQ&type=Common Stock&currency=USD"

    usa, created = Country.objects.get_or_create(name="United States")
    us_dollar, created = Currency.objects.get_or_create(name="USD")

    response = requests.get(api_url)
    stocks_json = response.json()["data"]
    for i in range(0, len(stocks_json), 50):
        stock_data = stocks_json[i]
        stock = StockData(
            symbol=stock_data.get("symbol"),
            name=stock_data.get("name"),
            exchange=stock_data.get("exchange"),
            type=StockData.StockType.COMMON_STOCK,
            currency=us_dollar,
            country=usa,
        )
        stock.save()


if __name__ == "__main__":
    load_data()
