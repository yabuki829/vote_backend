# Generated by Django 4.1 on 2023-05-17 12:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_user_lastaccess'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='lastAccess',
            field=models.DateField(default=datetime.datetime(2023, 5, 17, 12, 5, 23, 705579, tzinfo=datetime.timezone.utc)),
        ),
    ]
