# Generated by Django 3.2.8 on 2021-10-27 17:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20211027_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailotp',
            name='expT',
            field=models.CharField(default=1635357615, max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.IntegerField(default=3),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='expT',
            field=models.CharField(default=1635357615, max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.CharField(default=datetime.datetime(2021, 10, 27, 17, 45, 15, 818448), max_length=50, null=True),
        ),
    ]
