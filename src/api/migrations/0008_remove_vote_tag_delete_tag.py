# Generated by Django 4.1.1 on 2023-05-06 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='tag',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]