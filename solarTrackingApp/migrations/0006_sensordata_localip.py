# Generated by Django 4.2.1 on 2024-03-03 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solarTrackingApp', '0005_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensordata',
            name='localIp',
            field=models.CharField(default='', max_length=20),
        ),
    ]
