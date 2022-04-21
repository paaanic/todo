# Generated by Django 4.0.3 on 2022-04-19 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
        ('tasks', '0008_taskshare_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, max_length=255)),
                ('datetime', models.DateTimeField()),
                ('dispatch_user_id', models.CharField(max_length=255)),
                ('dispatchers', models.ManyToManyField(related_name='notifications', to='notifications.dispatcher')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='tasks.task')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]