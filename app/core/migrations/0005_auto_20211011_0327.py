# Generated by Django 3.2.8 on 2021-10-11 03:27

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_test_add_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddOrderPendingEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('sent', 'sent'), ('failed', 'failed')], default='pending', max_length=10)),
                ('email', models.EmailField(max_length=254)),
                ('order_id', models.CharField(max_length=50)),
                ('reference', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AddPendingEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('sent', 'sent'), ('failed', 'failed')], default='pending', max_length=10)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='AddPendingEmail2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('sent', 'sent'), ('failed', 'failed')], default='pending', max_length=10)),
                ('subject', models.CharField(max_length=200)),
                ('notes', models.TextField()),
                ('tablename', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='BillingDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField()),
                ('apartment', models.CharField(max_length=200)),
                ('notes', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon', models.CharField(max_length=30)),
                ('discount', models.IntegerField()),
                ('used', models.BooleanField(default=False)),
                ('seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('sent', 'sent'), ('failed', 'failed')], default='pending', max_length=10)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('seen', models.BooleanField(default=False)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='EmailOtp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('used', models.BooleanField(default=False)),
                ('expd', models.BooleanField(default=False)),
                ('expT', models.CharField(default=1633923734, max_length=50)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('item_id', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('delivery_type', models.CharField(choices=[('cash', 'cash'), ('card', 'card')], max_length=10)),
                ('price', models.FloatField()),
                ('order_id', models.CharField(max_length=50)),
                ('total', models.FloatField()),
                ('delivery_fee', models.FloatField()),
                ('image', models.TextField()),
                ('reference', models.CharField(max_length=50)),
                ('price_desc', models.CharField(max_length=50)),
                ('seen', models.BooleanField(default=False)),
                ('duration', models.IntegerField()),
                ('delivery_status', models.CharField(choices=[('process', 'process'), ('delivered', 'delivered'), ('procpendingess', 'pending')], default='process', max_length=20)),
                ('quantity', models.IntegerField()),
                ('paid', models.CharField(choices=[('pending', 'pending'), ('paid', 'paid'), ('not_paid', 'not_paid')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('discount', models.IntegerField()),
                ('rating', models.IntegerField(default=3)),
                ('rating1', models.IntegerField(default=10)),
                ('rating2', models.IntegerField(default=10)),
                ('rating3', models.IntegerField(default=10)),
                ('rating4', models.IntegerField(default=10)),
                ('rating5', models.IntegerField(default=10)),
                ('purchase', models.IntegerField(default=0)),
                ('image', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('seen', models.BooleanField(default=False)),
                ('sPrice', models.FloatField()),
                ('mPrice', models.FloatField()),
                ('lPrice', models.FloatField()),
                ('sPrice_desc', models.CharField(max_length=50)),
                ('mPrice_desc', models.CharField(max_length=50)),
                ('lPrice_desc', models.CharField(max_length=50)),
                ('duration', models.IntegerField()),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.category')),
            ],
        ),
        migrations.CreateModel(
            name='ResetPassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('used', models.BooleanField(default=False)),
                ('expd', models.BooleanField(default=False)),
                ('expT', models.CharField(default=1633923734, max_length=50)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('description', models.TextField()),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, size=None)),
                ('description', models.TextField()),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('quantity', models.IntegerField(default=0)),
                ('seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('deadline', models.DateTimeField()),
                ('subject', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('completed', 'completed'), ('expired', 'expired'), ('declined', 'declined')], default='pending', max_length=10)),
                ('seen', models.BooleanField(default=False)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Top_up',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('description', models.TextField()),
                ('sub_total', models.FloatField()),
                ('image', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('order_id', models.CharField(max_length=50)),
                ('total', models.FloatField()),
                ('seen', models.BooleanField(default=False)),
                ('pay_type', models.CharField(choices=[('paystack', 'paystack'), ('flutterwave', 'flutterwave')], max_length=15)),
                ('reference', models.CharField(max_length=50)),
                ('channel', models.CharField(max_length=20)),
                ('brand', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('paid', 'paid'), ('not_paid', 'not_paid')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='user',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='disabled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deactivate_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='pass_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='purchase',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('superUser', 'superUser'), ('admin', 'admin'), ('rider', 'rider')], default='user', max_length=10),
        ),
        migrations.AddField(
            model_name='user',
            name='seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='subscribe_news',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activate_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.DeleteModel(
            name='Test',
        ),
        migrations.AddField(
            model_name='wishlist',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product'),
        ),
        migrations.AddField(
            model_name='task',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='specialorder',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='review',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='review',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orders',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orders',
            name='billing_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.billingdetails'),
        ),
        migrations.AddField(
            model_name='orders',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.category'),
        ),
        migrations.AddField(
            model_name='orders',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orders',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product'),
        ),
        migrations.AddField(
            model_name='orders',
            name='top_up',
            field=models.ManyToManyField(related_name='top_up', to='core.Top_up'),
        ),
        migrations.AddField(
            model_name='notification',
            name='edit_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coupon',
            name='created_for',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactus',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='billingdetails',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
