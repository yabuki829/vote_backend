# Generated by Django 4.1 on 2023-05-17 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_rename_isonlyloginuser_vote_islimitedrelease'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthOfDay',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.IntegerField(default=0),
        ),
    ]
