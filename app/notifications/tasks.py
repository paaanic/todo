from django.apps import apps
from celery import shared_task



@shared_task
def create_notification(dispatcher_id, notification_id, app_label, model):
    notification_model = apps.get_model(app_label, model)
    notification = notification_model.objects.get(id=notification_id)
    Dispatcher = apps.get_model('notifications.Dispatcher')
    dispatcher = Dispatcher.objects.get(id=dispatcher_id)
    dispatcher.dispatch(notification)
