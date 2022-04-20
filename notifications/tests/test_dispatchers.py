from django.test import SimpleTestCase

from ..dispatchers import BaseDispatcher, TelegramDispatcher


class BaseDispatcherTest(SimpleTestCase):
    def test_dispatch(self):
        with self.assertRaises(TypeError):
            BaseDispatcher.dispatch(None)


class TelegramDispatcher:
    def test_dispatch(self):
        pass

    def test_send_message(self):
        pass