# Generated by Django 3.2.8 on 2021-10-29 01:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20211028_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailotp',
            name='expT',
            field=models.CharField(default=1635471358, max_length=50),
        ),
        migrations.AlterField(
            model_name='notification',
            name='item_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='expT',
            field=models.CharField(default=1635471358, max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.CharField(default=datetime.datetime(2021, 10, 29, 1, 20, 58, 288877), max_length=50, null=True),
        ),
    ]
