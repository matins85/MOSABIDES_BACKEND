# Generated by Django 3.2.8 on 2021-10-28 22:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20211027_1745'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='image',
        ),
        migrations.AlterField(
            model_name='emailotp',
            name='expT',
            field=models.CharField(default=1635462002, max_length=50),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='expT',
            field=models.CharField(default=1635462002, max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.CharField(default=datetime.datetime(2021, 10, 28, 22, 45, 2, 481323), max_length=50, null=True),
        ),
    ]