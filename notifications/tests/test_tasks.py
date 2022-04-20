from datetime import timedelta
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from .utils import AbstractModelMixin
from ..models import BaseNotification, Dispatcher
from ..tasks import create_notification


class MockNotification:
    pass


class TestCreateNotification(AbstractModelMixin, TestCase):

    abstract_model = BaseNotification

    def setUp(self):
        self.notif = self.model.objects.create(
            datetime=timezone.now()+timedelta(minutes=1)
        )

    @mock.patch.object(Dispatcher, 'dispatch')
    def test_success(self, mock_dispatch):
        model_type = ContentType.objects.get_for_model(self.model)
        dispatcher_id = 1
        create_notification(
            dispatcher_id,
            self.notif.pk,
            model_type.app_label,
            model_type.model
        )
        mock_dispatch.assert_called_with(self.notif)

