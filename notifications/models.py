from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from celery import group

from .dispatchers import TelegramDispatcher
from .tasks import create_notification


class Dispatcher(models.Model):

    class DispatcherType(models.TextChoices):
        TELEGRAM = 'TG'

    _DISPATCHERS_BY_TYPE = {
       DispatcherType.TELEGRAM: TelegramDispatcher,
    }

    type = models.CharField(
        max_length=2,
        choices=DispatcherType.choices,
        default=DispatcherType.TELEGRAM,
        unique=True
    )

    def __str__(self):
        return self.DispatcherType(self.type).label

    def dispatch(self, notification):
        dispatcher = self._get_dispatcher_by_type(self.type)
        dispatcher.dispatch(notification)

    @classmethod
    def _get_dispatcher_by_type(cls, type):
        try:
            return cls._DISPATCHERS_BY_TYPE[type]
        except KeyError:
            raise ValueError("No dispatcher implementation defined for this type")


class BaseNotification(models.Model):
    message = models.TextField(max_length=500, blank=True)
    datetime = models.DateTimeField()
    dispatchers = models.ManyToManyField(
        Dispatcher, related_name='notifications'
    )
    dispatch_user_id = models.CharField(max_length=255)
    task_group_id = models.UUIDField(null=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.datetime <= timezone.now():
            raise ValidationError("Notification datetime cannot be in past")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def register(self):
        model_type = ContentType.objects.get_for_model(self)
        args_ = self.id, model_type.app_label, model_type.model
        tasks = [
            create_notification.s(dispatcher.id, *args_)
            for dispatcher in self.dispatchers.all()
        ]
        task_group = group(
            tasks, eta=self.datetime, acks_late=True, ignore_result=True
        )
        task_group()
        self.task_group_id = task_group.id
