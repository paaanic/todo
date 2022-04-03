# Generated by Django 4.0.3 on 2022-04-03 11:49

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('friendships', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendshipUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='friendshiprequest',
            name='message',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
