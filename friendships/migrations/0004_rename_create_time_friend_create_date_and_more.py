# Generated by Django 4.0.3 on 2022-04-03 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friendships', '0003_friend_create_time_friendshiprequest_create_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friend',
            old_name='create_time',
            new_name='create_date',
        ),
        migrations.RenameField(
            model_name='friendshiprequest',
            old_name='create_time',
            new_name='create_date',
        ),
    ]