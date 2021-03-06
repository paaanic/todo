# Generated by Django 4.0.3 on 2022-04-03 14:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('friendships', '0002_friendshipuser_friendshiprequest_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='friendshiprequest',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
