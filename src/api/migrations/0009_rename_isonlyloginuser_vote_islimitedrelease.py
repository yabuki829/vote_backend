# Generated by Django 4.1 on 2023-05-07 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_remove_vote_tag_delete_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='isOnlyLoginUser',
            new_name='isLimitedRelease',
        ),
    ]
