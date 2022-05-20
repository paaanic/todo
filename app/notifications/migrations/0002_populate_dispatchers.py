from django.db import migrations

from ..models import Dispatcher


def populate_dispatchers(apps, schema_editor):
    for type_choice in Dispatcher.DispatcherType.values:
        obj = Dispatcher(type=type_choice)
        obj.save()


def depopulate_dispatchers(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0001_initial')
    ]

    operations = [
        migrations.RunPython(populate_dispatchers, depopulate_dispatchers)
    ]
