import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class StockConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)("market", self.channel_name)
        self.accept()

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))
