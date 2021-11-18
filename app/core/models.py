from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings
# from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta
import time
from jsonfield import JSONField
from django.utils import timezone


# Create your models here.
now = timezone.now
now2 = datetime.now()

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
           ('superAdmin', 'superAdmin'),
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
    pass_id = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=10, choices=UserRole, default='user')
    phone = models.CharField(max_length=20, null=True, blank=True)
    subscribe_news = models.BooleanField(default=False)
    purchase = models.IntegerField(default=0)
    seen = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)
    last_login = models.DateTimeField(default=now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
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
    created_at = models.CharField(max_length=50, default=now2, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'



class Category(models.Model):
    """Product category for food"""
    name = models.CharField(max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name


class EmailOtp(models.Model):
    code = models.CharField(max_length=10, null=False, blank=False)
    used = models.BooleanField(default=False)
    expd = models.BooleanField(default=False)
    expT = models.CharField(max_length=50, default=one_t)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return self.code


class ResetPassword(models.Model):
    code = models.CharField(max_length=10, null=False, blank=False)
    used = models.BooleanField(default=False)
    expd = models.BooleanField(default=False)
    expT = models.CharField(max_length=50, default=one_t, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return self.code


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True, null=False, blank=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, null=False, blank=False)
    price = models.FloatField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    rating = models.IntegerField(default=3)
    rating1 = models.IntegerField(default=10)
    rating2 = models.IntegerField(default=10)
    rating3 = models.IntegerField(default=10)
    rating4 = models.IntegerField(default=10)
    rating5 = models.IntegerField(default=10)
    purchase = models.IntegerField(default=0)
    # image = ArrayField(models.TextField(), blank=False)
    image = JSONField(null=False, blank=False)
    seen = models.BooleanField(default=False)
    sPrice = models.FloatField(null=True, blank=True)
    mPrice = models.FloatField(null=True, blank=True)
    lPrice = models.FloatField(null=True, blank=True)
    sPrice_desc = models.CharField(max_length=50, null=True, blank=True)
    mPrice_desc = models.CharField(max_length=50, null=True, blank=True)
    lPrice_desc = models.CharField(max_length=50, null=True, blank=True)
    duration = models.IntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.product_name


class ContactUs(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.email


class SpecialOrder(models.Model):
    # image = ArrayField(models.TextField(), blank=True)
    image = JSONField()
    description = models.TextField(null=False, blank=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(null=False, blank=False)
    quantity = models.IntegerField(default=0)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.email



class Wishlist(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.created_by)


class Task(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    deadline = models.DateTimeField(null=False, blank=False)
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=task_status, default='pending')
    seen = models.BooleanField(default=False)
    description = models.TextField(null=False, blank=False)

    def __str__(self):
        return str(self.created_by)


class BillingDetails(models.Model):
    """Billing details used for food delivery"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.TextField(null=False, blank=False)
    apartment = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Notification(models.Model):
    subject = models.CharField(max_length=200, null=True, blank=True)
    item_id = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(default=now)
    seen = models.BooleanField(default=False)
    edit_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.subject


# class Top_up(models.Model):
#     name = models.CharField(max_length=200)
#     price = models.FloatField()
#     quantity = models.IntegerField()
#     description = models.TextField()
#     sub_total = models.FloatField()
#     image = models.TextField()
    

class Orders(models.Model):
    product_name = models.CharField(max_length=200, null=False, blank=False)    
    delivery_type = models.CharField(max_length=10, choices=delivery_type, null=False, blank=False)
    category = models.CharField(max_length=50, null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    order_id = models.CharField(max_length=50, null=False, blank=False)
    total = models.FloatField(null=False, blank=False)
    paid = models.BooleanField(default=False)
    delivery_fee = models.FloatField(null=False, blank=False)
    reference = models.CharField(max_length=50)
    price_desc = models.CharField(max_length=50)
    seen = models.BooleanField(default=False)
    duration = models.IntegerField(null=False, blank=False)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    billing_id = models.ForeignKey('BillingDetails', on_delete=models.SET_NULL, null=True)
    delivery_status = models.CharField(max_length=20, choices=DELV, default='process')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
            null=True, related_name='assigned_to')
    # top_up = models.ManyToManyField(Top_up, related_name='top_up')
    top_up = JSONField(null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    paid_status = models.CharField(max_length=10, choices=PAID, default='pending')
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
            related_name='created_by')

    def __str__(self):
        return str(self.product_name)



# class Orders(models.Model):
#     product_name = models.CharField(max_length=200, null=False, blank=False)    
#     delivery_type = models.CharField(max_length=10, choices=delivery_type, null=False, blank=False)
#     category = models.CharField(max_length=50, null=False, blank=False)
#     price = models.FloatField(null=False, blank=False)
#     order_id = models.CharField(max_length=50, null=False, blank=False)
#     total = models.FloatField(null=False, blank=False)
#     paid = models.BooleanField(default=False)
#     delivery_fee = models.FloatField(null=False, blank=False)
#     price_desc = models.CharField(max_length=50)
#     duration = models.IntegerField(null=False, blank=False)
#     product_id = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
#     billing_id = models.ForeignKey('BillingDetails', on_delete=models.SET_NULL, null=True)
#     delivery_status = models.CharField(max_length=20, choices=DELV, default='process')
#     assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
#             null=True, related_name='assigned_to')
#     top_up = JSONField(null=False, blank=False)
#     quantity = models.IntegerField(null=False, blank=False)
#     paid_status = models.CharField(max_length=10, choices=PAID, default='pending')
#     created_at = models.DateTimeField(default=now)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
#             related_name='created_by')

#     def __str__(self):
#         return str(self.product_name)



class Coupon(models.Model):
    coupon = models.CharField(max_length=30, null=False, blank=False)
    discount = models.IntegerField(null=False, blank=False)
    used = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    created_for = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return self.coupon


class EmailMessage(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=200)
    seen = models.BooleanField(default=False)
    body = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.email


class AddPendingEmail(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.status


class AddOrderPendingEmail(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    email = models.EmailField(null=False, blank=False)
    order_id = models.CharField(max_length=50, null=False, blank=False)
    reference = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.status



class AddPendingEmail2(models.Model):
    status = models.CharField(max_length=10, choices=email_status, default='pending')
    subject = models.CharField(max_length=200, null=False, blank=False)
    notes = models.TextField(null=False, blank=False)
    tablename = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.status


class Review(models.Model):
    rating = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=False, blank=False)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.email


class Transactions(models.Model):
    product_name = models.CharField(max_length=200, null=False, blank=False)
    order_id = models.CharField(max_length=50, null=False, blank=False)
    total = models.FloatField(null=False, blank=False)
    seen = models.BooleanField(default=False)
    pay_type = models.CharField(max_length=15, choices=pay_type)
    reference = models.CharField(max_length=50, null=False, blank=False)
    channel = models.CharField(max_length=20, null=True, blank=True)
    brand = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=PAID)

    def __str__(self):
        return self.product_name


class AuthToken(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField(null=False, blank=False)
    access = models.BooleanField(default=False, null=False, blank=False)
    refresh = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return str(self.created_by)


class Test(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    