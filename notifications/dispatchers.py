import requests
from abc import ABC, abstractmethod

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class BaseDispatcher(ABC):
    @classmethod
    @abstractmethod
    def dispatch(cls, notification):
        pass


class TelegramDispatcher(BaseDispatcher):
    _API_URL = 'https://api.telegram.org/'

    @classmethod
    def dispatch(cls, notification):
        try:
            getattr(settings, 'NOTIFICATIONS_TELEGRAM_BOT_TOKEN')
        except AttributeError:
            raise ImproperlyConfigured(
                "You have to set NOTIFICATIONS_TELEGRAM_BOT_TOKEN in django settings before using this"
            )

        if notification.dispatch_user_id is None:
            raise ValueError("You have to set 'dispatch_user_id' before using this method")
            
        try:
            cls._send_message(
                notification.dispatch_user_id, notification.comment
            )
        finally:
            notification.delete()

    @classmethod
    def _send_message(cls, chat_id, msg):
        endpoint = \
            f'bot{settings.NOTIFICATIONS_TELEGRAM_BOT_TOKEN}/sendMessage'
        requests.post(
            cls._API_URL + endpoint,
            params={'chat_id': chat_id, 'text': msg}
        )