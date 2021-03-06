# Generated by Django 3.2.8 on 2021-10-24 00:50

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20211023_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='emailotp',
            name='expT',
            field=models.CharField(default=1635037525, max_length=50),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='expT',
            field=models.CharField(default=1635037525, max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.CharField(default=datetime.datetime(2021, 10, 24, 0, 50, 25, 824617), max_length=50, null=True),
        ),
    ]
