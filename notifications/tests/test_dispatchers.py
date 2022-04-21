from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from ..dispatchers import BaseDispatcher, TelegramDispatcher
from ..models import BaseNotification


class BaseDispatcherTest(SimpleTestCase):
    def test_dispatch(self):
        with self.assertRaises(NotImplementedError):
            BaseDispatcher.dispatch(None)


class TelegramDispatcherTest(SimpleTestCase):
    def setUp(self):
        self.mock__send_message = mock.patch.object(
            TelegramDispatcher, '_send_message'
        )

    def test_dispatch(self):
        def _mock_init(self, verbose_name=None, **kwargs):
            self.__dict__.update(kwargs)

        mock_init = mock.patch.object(
            BaseNotification, '__init__', _mock_init
        )

        with mock_init:
            notif = BaseNotification(
                dispatch_user_id='1', message="Test message"
            )
            with mock.patch.object(notif, 'delete'):
                TelegramDispatcher.dispatch(notif)
                notif.delete.assert_called_once()
        
    def test_send_message(self):
        msg = "Test message"
        with self.mock__send_message:
            TelegramDispatcher._send_message(None, msg)
            TelegramDispatcher._send_message.assert_called_once_with(None, msg)
