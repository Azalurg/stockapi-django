from time import sleep

from celery import shared_task
from django.conf import settings
import requests

from stockApp.models import StockData, StockTimeSeriesData


@shared_task
def get_stock_time_series(stock_symbol):
    base_url = (
        "https://api.twelvedata.com/time_series?symbol={}&interval=1day&apikey={}"
    )
    api_key = getattr(settings, "TWELVEDATA_API_KEY", None)
    stock = StockData.objects.filter(symbol=stock_symbol).first()

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

    return 0


@shared_task
def get_all_stocks_time_series():
    stocks = list(StockData.objects.all())

    for stock in stocks:
        get_stock_time_series.delay(stock.symbol)
        sleep(10)
    return 0
