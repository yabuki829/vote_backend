# Generated by Django 4.1 on 2023-04-28 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_profile_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='explain',
            field=models.CharField(default='nothing', max_length=100),
        ),
    ]
