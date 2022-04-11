# Generated by Django 4.0.3 on 2022-04-11 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_taskshare_unique_task_share'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasknotification',
            name='task',
        ),
        migrations.RemoveConstraint(
            model_name='taskshare',
            name='unique_task_share',
        ),
        migrations.AddConstraint(
            model_name='taskshare',
            constraint=models.UniqueConstraint(fields=('task', 'to_user'), name='unique_task_share'),
        ),
        migrations.DeleteModel(
            name='TaskNotification',
        ),
    ]
