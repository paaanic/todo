from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from notifications.models import BaseNotification


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
    
    def complete(self):
        now = timezone.now()

        for share in self.shares.all():
            share.done = True
            share.done_date = now

        self.done = True
        self.done_date = now

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
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_task_shares'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_shares'
    )
    comment = models.CharField(max_length=255, blank=True)
    done = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['task', 'to_user'],
                name='unique_task_share'
            )
        ]

    @property
    def active(self):
        return not self.done and self.task.active

    def __str__(self):
        return f'{self.from_user} shares {self.task} with {self.to_user}'

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("You can't share tasks with yourself")
        elif self.to_user == self.task.author:
            raise ValidationError("You can't share a task with it's author")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TaskNotification(BaseNotification):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    def clean(self):
        super().clean()
        try:
            self.message = f"Notification on {self.task.title}"
        except:
            pass