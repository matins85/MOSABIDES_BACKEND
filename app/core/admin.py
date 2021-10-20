from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from core import models
# Register your models here.
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name', 'disabled', 'role', 'phone',
        'subscribe_news', 'purchase', 'phone', 'image', 'last_login', 
        'disabled_by', 'password', 'updated_by', 'created_at', 'pass_id', 'seen']
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login','created_at',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'disabled', 'role', 'phone',
        'subscribe_news', 'purchase', 'phone', 'image', 'last_login', 
        'disabled_by', 'password', 'updated_by', 'created_at', 'pass_id', 'seen')
        }),
    )



admin.site.unregister(Group)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Category)
admin.site.register(models.ContactUs)
admin.site.register(models.EmailMessage)
admin.site.register(models.EmailOtp)
admin.site.register(models.Notification)
admin.site.register(models.Orders)
admin.site.register(models.Product)
admin.site.register(models.ResetPassword)
admin.site.register(models.Review)
admin.site.register(models.SpecialOrder)
admin.site.register(models.Task)
admin.site.register(models.AuthToken)
admin.site.register(models.Transactions)
admin.site.register(models.Wishlist)
admin.site.register(models.AddOrderPendingEmail)
admin.site.register(models.AddPendingEmail2)
admin.site.register(models.AddPendingEmail)
admin.site.register(models.BillingDetails)
admin.site.register(models.Coupon)


