from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta
import time
from django.utils import timezone


# Create your models here.
now = timezone.now

PAID = (
    ('pending', 'pending'),
    ('paid', 'paid'),
    ('not_paid', 'not_paid'),
)

email_status = (
    ('pending', 'pending'),
    ('sent', 'sent'),
    ('failed', 'failed'),
)

DELV = (
    ('process', 'process'),
    ('delivered', 'delivered'),
    ('procpendingess', 'pending'),
)

delivery_type = (
    ('cash', 'cash'),
    ('card', 'card'),
)

UserRole = (('user', 'user'),
           ('superUser', 'superUser'),
           ('admin', 'admin'),
           ('rider', 'rider'),
)

task_status = ((
    ('pending', 'pending'),
    ('completed', 'completed'),
    ('expired', 'expired'),
    ('declined', 'declined'),
    )
)

pay_type = ((
    ('paystack', 'paystack'),
    ('flutterwave', 'flutterwave'),
    )
)

one_t = int(time.time()) + 900


class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and saves a new user"""
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Create user model thats support using email insttead of username"""
    email = models.EmailField(max_length=200, unique=True, null=True, blank=False)
    # firstname = models.CharField(max_length=200, null=True)
    # lastname = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True, blank=False)
    pass_id = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=10, choices=UserRole, default='user')
    phone = models.CharField(max_length=20, null=True, blank=True)
    subscribe_news = models.BooleanField(default=False)
    purchase = models.IntegerField(default=0)
    seen = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)
    last_login = models.DateTimeField(default=now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    password = models.CharField(max_length=200, null=True, blank=True)
    # tasks = models.ManyToManyField(Task,null=True, related_name='tasks')
    # orders = models.ManyToManyField(Orders, null=True, related_name='orders')
    # wishlist = models.ManyToManyField(Wishlist, null=True, related_name='wishlist')
    # billing = models.ManyToManyField(BillingDetails, null=True, related_name='billing')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
            blank=True, related_name='activate_by')
    disabled = models.BooleanField(default=False)
    disabled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
            blank=True, related_name='deactivate_by')
    created_at = models.DateTimeField(default=now)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Category(models.Model):
    """Product category for food"""
    name = models.CharField(max_length=50,null=False,blank=False)
    created_at = models.DateTimeField(default=now)


class EmailOtp(models.Model):
    code = models.CharField(max_length=10)
    used = models.BooleanField(default=False)
    expd = models.BooleanField(default=False)
    expT = models.CharField(max_length=50, default=one_t)
    email = models.EmailField()


class ResetPassword(models.Model):
    code = models.CharField(max_length=10)
    used = models.BooleanField(default=False)
    expd = models.BooleanField(default=False)
    expT = models.CharField(max_length=50, default=one_t)
    email = models.EmailField()


class Product(models.Model):
    product_name = models.CharField(max_length=200, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, null=False, blank=False)
    price = models.FloatField()
    discount = models.IntegerField()
    rating = models.IntegerField(default=3)
    rating1 = models.IntegerField(default=10)
    rating2 = models.IntegerField(default=10)
    rating3 = models.IntegerField(default=10)
    rating4 = models.IntegerField(default=10)
    rating5 = models.IntegerField(default=10)
    purchase = models.IntegerField(default=0)
    image = ArrayField(models.TextField(), blank=False)
    seen = models.BooleanField(default=False)
    sPrice = models.FloatField()
    mPrice = models.FloatField()
    lPrice = models.FloatField()
    sPrice_desc = models.CharField(max_length=50)
    mPrice_desc = models.CharField(max_length=50)
    lPrice_desc = models.CharField(max_length=50)
    duration = models.IntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    description = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class SpecialOrder(models.Model):
    image = ArrayField(models.TextField(), blank=True)
    description = models.TextField()
    name = models.CharField(max_length=255)
    email = models.EmailField()
    quantity = models.IntegerField(default=0)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)



class Wishlist(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)


class Task(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    deadline = models.DateTimeField()
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=task_status, default='pending')
    seen = models.BooleanField(default=False)
    description = models.TextField()


class BillingDetails(models.Model):
    """Billing details used for food delivery"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.TextField()
    apartment = models.CharField(max_length=200)
    notes = models.CharField(max_length=255)


class Notification(models.Model):
    subject = models.CharField(max_length=200)
    item_id = models.IntegerField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(default=now)
    edit_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class Top_up(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()
    description = models.TextField()
    sub_total = models.FloatField()
    image = models.TextField()
    

class Orders(models.Model):
    product_name = models.CharField(max_length=200)    
    delivery_type = models.CharField(max_length=10, choices=delivery_type)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.FloatField()
    order_id = models.CharField(max_length=50)
    total = models.FloatField()
    paid = models.BooleanField(default=False)
    delivery_fee = models.FloatField()
    image = models.TextField()
    reference = models.CharField(max_length=50)
    price_desc = models.CharField(max_length=50)
    seen = models.BooleanField(default=False)
    duration = models.IntegerField()
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    billing_id = models.ForeignKey(BillingDetails, on_delete=models.SET_NULL, null=True)
    delivery_status = models.CharField(max_length=20, choices=DELV, default='process')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
            null=True, related_name='assigned_to')
    top_up = models.ManyToManyField(Top_up, related_name='top_up')
    quantity = models.IntegerField()
    paid = models.CharField(max_length=10, choices=PAID, default='pending')
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
            related_name='created_by')



class Coupon(models.Model):
    coupon = models.CharField(max_length=30)
    discount = models.IntegerField()
    used = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    created_for = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField()


class EmailMessage(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    seen = models.BooleanField(default=False)
    body = models.TextField()
    created_at = models.DateTimeField(default=now)


class AddPendingEmail(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    email = models.EmailField()
    subject = models.CharField(max_length=200)


class AddOrderPendingEmail(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    email = models.EmailField()
    order_id = models.CharField(max_length=50)
    reference = models.CharField(max_length=50)



class AddPendingEmail2(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    subject = models.CharField(max_length=200)
    notes = models.TextField()
    tablename = models.CharField(max_length=50)


class Review(models.Model):
    rating = models.IntegerField()
    description = models.TextField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    seen = models.BooleanField(default=False)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)




class Transactions(models.Model):
    product_name = models.CharField(max_length=200)
    order_id = models.CharField(max_length=50)
    total = models.FloatField()
    seen = models.BooleanField(default=False)
    pay_type = models.CharField(max_length=15, choices=pay_type)
    reference = models.CharField(max_length=50)
    channel = models.CharField(max_length=20)
    brand = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=PAID)
