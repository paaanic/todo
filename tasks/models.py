from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.CharField(max_length=100, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, null=True)
    done = models.BooleanField(default=False)
    done_date = models.DateTimeField(default=None, null=True)

    @property
    def active(self):
        return (
            not self.done and
            (self.expire_date is None or (timezone.now() <= self.expire_date))
        )

    @property
    def failed(self):
        return not (self.done or self.active)

    def __str__(self):
        return self.title

    def clean(self):
        create_date = (self.create_date if self.create_date is not None 
                                        else timezone.now())
        if self.expire_date and self.expire_date <= create_date:
            raise ValidationError(
                'Task expiration date cannot be from the past'
            )
        
        if not self.done and self.done_date is not None:
            raise ValidationError(
                'Task done date cannot be filled when task is not done'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TaskShare(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} shares {self.task}'


class TaskNotification(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    dt_before_expire = models.DurationField()

    def __str__(self):
        return f'{self.dt_before_expire} before {self.task.expire_date}'

    def clean(self):
        if self.task.expire_date is None:
            raise ValidationError(
                'You cannot add notifications to tasks with no expire_date ' 
                'specified'
            )
        if self.task.done or self.task.failed:
            raise ValidationError(
                'You cannot add notifications to failed or done tasks'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
