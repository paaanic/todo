from datetime import timedelta
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .utils import AbstractModelMixin
from ..models import BaseNotification, Dispatcher


class MockManyRelatedManager:
    def __init__(self, *args, **kwargs):
        self.related_objects = []

    def add(self, obj):
        self.related_objects.append(obj)

    def count(self):
        return len(self.related_objects)


class TestNotificationMixin(AbstractModelMixin):
    abstract_model = BaseNotification

    def setUp(self):
        self.test_notif_kwargs = {
            'comment': "Test comment",
            'datetime': timezone.now()+timedelta(minutes=1)
        }


class BaseNotificationModelTest(TestNotificationMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_create(self):
        with self.assertRaises(TypeError):
            BaseNotification(**self.test_notif_kwargs)
        self.model.objects.create(**self.test_notif_kwargs)
        notif = self.model.objects.last()
        self.assertEqual(notif.comment, self.test_notif_kwargs['comment'])
        self.assertEqual(notif.datetime, self.test_notif_kwargs['datetime'])

    def test_str(self):
        notif = self.model.objects.create(**self.test_notif_kwargs)
        self.assertEqual(str(notif), f"Notification: {notif.comment}")
        del self.test_notif_kwargs['comment']
        notif_with_no_comment = \
            self.model.objects.create(**self.test_notif_kwargs)
        self.assertEqual(
            str(notif_with_no_comment),
            f"Notification: no comment provided"
        )

    def test_clean(self):
        notif = self.model(**self.test_notif_kwargs)
        notif.clean()
        past_time = timezone.now() - timedelta(seconds=1)
        self.test_notif_kwargs['datetime'] = past_time
        notif = self.model(**self.test_notif_kwargs)
        with self.assertRaises(ValidationError):
            notif.clean()

    def test_save(self):
        notif = self.model(**self.test_notif_kwargs)
        notif.save()
        self.assertEqual(notif, self.model.objects.last())

    def test_add_dispatcher(self):
        notif = self.model.objects.create(**self.test_notif_kwargs)
        dispatcher = Dispatcher.objects.get(id=1)
        with mock.patch.object(
            self.model, 'dispatchers', MockManyRelatedManager()
        ):
            notif.dispatchers.add(dispatcher)
            self.assertEqual(notif.dispatchers.count(), 1)

    @mock.patch.object(Dispatcher, 'dispatch') 
    def test_register(self, mock_dispatch):
        notif = self.model.objects.create(**self.test_notif_kwargs)
        mock_dispatchers = mock.patch.object(
            self.model, 'dispatchers', Dispatcher.objects
        )
        mock_group_call = mock.patch('celery.group.__call__')
        with mock_dispatchers, mock_group_call:
            notif.register()


class DispatcherModelTest(TestNotificationMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.notif_model = cls.model

    def test_initial_data(self):
        for dispatcher_type in Dispatcher.DispatcherType.values:
            try:
                Dispatcher.objects.get(type=dispatcher_type)
            except Dispatcher.DoesNotExist:
                self.fail(
                    f"Dispatcher of type {dispatcher_type} was not initiated"
                )

    def test_dispatch(self):
        notif = self.notif_model.objects.create(**self.test_notif_kwargs)
        for dispatcher_obj in Dispatcher.objects.all():
            dispatcher = Dispatcher._get_dispatcher_by_type(
                dispatcher_obj.type
            )
            with mock.patch.object(dispatcher, 'dispatch') as mock_dispatch:
                dispatcher_obj.dispatch(notif)
                mock_dispatch.assert_called_once_with(notif)

    def test__get_dispatcher_by_type(self):
        for dispatcher_type in Dispatcher.DispatcherType.values:
            try:
                Dispatcher._get_dispatcher_by_type(dispatcher_type)
            except ValueError as e:
                self.fail(str(e))
