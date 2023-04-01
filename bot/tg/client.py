import os

import requests

from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse

BOT_TOKEN = os.getenv("BOT_TOKEN")


class TgClient:
    def __init__(self, token: str = None):
        self.token = token if token else BOT_TOKEN

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url('getUpdates')
        response = requests.get(url, params={'offset': offset, 'timeout': timeout})
        return GetUpdatesResponse(**response.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url('sendMessage')
        response = requests.get(url, params={'chat_id': chat_id, 'text': text})
        return SendMessageResponse(**response.json())

