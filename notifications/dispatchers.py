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
        try:
            cls._send_message(notification.message)
        finally:
            notification.delete()

    @classmethod
    def _send_message(cls, msg):
        endpoint = \
            f'/bot{settings.NOTIFICATIONS_TELEGRAM_BOT_TOKEN}/sendMessage'
        requests.post(
            cls._API_URL + endpoint,
            params={'chat_id': '@maximspeshilov', 'text': msg}
        )