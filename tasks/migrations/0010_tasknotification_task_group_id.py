# Generated by Django 4.0.4 on 2022-04-20 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_tasknotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasknotification',
            name='task_group_id',
            field=models.UUIDField(null=True),
        ),
    ]
