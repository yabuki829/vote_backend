# Generated by Django 4.1 on 2023-05-18 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_tag_vote_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='tag',
            new_name='tags',
        ),
    ]
