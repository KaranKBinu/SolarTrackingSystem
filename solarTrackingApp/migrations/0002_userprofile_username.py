# Generated by Django 4.2.4 on 2024-01-30 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solarTrackingApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.EmailField(default='', max_length=254),
        ),
    ]