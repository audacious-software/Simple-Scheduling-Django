# pylint: skip-file
# Generated by Django 3.2.25 on 2025-05-16 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=1024, unique=True)),
                ('action', models.CharField(max_length=1024)),
                ('when', models.DateTimeField()),
                ('resolved', models.DateTimeField(blank=True, null=True)),
                ('context', models.JSONField(blank=True, default=dict)),
                ('outcome', models.CharField(choices=[('pending', 'Pending'), ('pause', 'Paused'), ('success', 'Success'), ('failure', 'Failure'), ('cancel', 'Canceled')], default='pending', max_length=4096)),
                ('outcome_log', models.TextField(blank=True, max_length=1048576, null=True)),
                ('fingerprint', models.CharField(max_length=1024)),
            ],
        ),
    ]
