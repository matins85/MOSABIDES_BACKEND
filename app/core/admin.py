from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from core import models


admin.site.site_header = "Mosabides Village Food Database"
admin.site.site_title = "Mosabides"
admin.site.index_title = "Mosabides Administration"


# Register your models here.
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['id', 'email', 'name', 'disabled', 'role', 'phone', 'disabled',
        'subscribe_news', 'purchase', 'phone', 'last_login', 
        'disabled_by', 'updated_by', 'created_at', 'seen',]
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role', 'phone', 'subscribe_news',
            'purchase', 'image', 'disabled_by', 'updated_by', 'pass_id', 'seen',
        )}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'disabled',)}
        ),
        (_('Important dates'), {'fields': ('last_login','created_at',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'disabled', 'role', 'phone',
        'subscribe_news', 'purchase', 'image', 'last_login', 
        'disabled_by', 'password', 'updated_by', 'created_at', 'pass_id', 'seen',)
        }),
    )


class ProductAdmin(admin.ModelAdmin):
    def change_category_to_default(self, request, queryset):
        queryset.update(category="default")

    ordering = ['id']
    list_display = ['product_name', 'category', 'rating', 'price', 'discount',]
    search_fields = ['product_name', 'id', 'category']
    actions = ['change_category_to_default',]
    list_editable = ['discount','rating',]
    list_filter = ['category', 'rating',]
    list_per_page = 50


class NotificationAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ['subject', 'item_id', 'email']
    list_filter = ['subject',]
    list_per_page = 50


admin.site.unregister(Group)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Category)
admin.site.register(models.ContactUs)
admin.site.register(models.EmailMessage)
admin.site.register(models.EmailOtp)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Orders)
admin.site.register(models.Product, ProductAdmin)
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



