# Generated by Django 4.0.3 on 2022-04-01 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_rename_is_done_task_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='done_date',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]