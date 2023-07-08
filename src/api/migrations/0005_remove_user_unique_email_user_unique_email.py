# Generated by Django 4.1.1 on 2023-05-01 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_thread_explain_alter_user_email_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='user',
            name='unique_email',
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(condition=models.Q(('email__isnull', False)), fields=('email',), name='unique_email'),
        ),
    ]