# Generated by Django 3.2.9 on 2021-11-28 21:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20211123_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailotp',
            name='expT',
            field=models.CharField(default=1638136179, max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='expT',
            field=models.CharField(default=1638136179, max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.CharField(default=datetime.datetime(2021, 11, 28, 21, 34, 39, 826636), max_length=50, null=True),
        ),
    ]
