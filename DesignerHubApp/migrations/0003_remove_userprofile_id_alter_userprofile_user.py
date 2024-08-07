# Generated by Django 5.0.6 on 2024-08-06 14:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DesignerHubApp', '0002_alter_userprofile_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='id',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_profile', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
