from time import sleep

from celery import shared_task
from django.conf import settings
import requests

from stockApp.models import StockData, StockTimeSeriesData


@shared_task
def get_stock_time_series():
    base_url = (
        "https://api.twelvedata.com/time_series?symbol={}&interval=1day&apikey={}"
    )
    api_key = getattr(settings, "TWELVEDATA_API_KEY", None)
    stocks = list(StockData.objects.all())

    for i, stock in enumerate(stocks):
        response = requests.get(base_url.format(stock.symbol, api_key))
        timeseries_json = response.json()["values"][0]
        timeseries_json["datetime"] = str(timeseries_json["datetime"]).split(" ")[0]
        StockTimeSeriesData.objects.get_or_create(
            stock=stock,
            open=timeseries_json["open"],
            high=timeseries_json["high"],
            low=timeseries_json["low"],
            close=timeseries_json["close"],
            volume=timeseries_json["volume"],
            date=timeseries_json["datetime"],
        )
        stock.last_time_series_update = timeseries_json["datetime"]
        stock.save()

        sleep(10)

    return 0
