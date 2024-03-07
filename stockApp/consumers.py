import json
from channels.generic.websocket import WebsocketConsumer


class StockConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({"message": "Connected"}))
