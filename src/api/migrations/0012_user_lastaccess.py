# Generated by Django 4.1 on 2023-05-17 12:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_user_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='lastAccess',
            field=models.DateField(default=datetime.datetime(2023, 5, 17, 12, 2, 3, 408555, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]