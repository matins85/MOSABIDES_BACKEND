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
    list_display = ['id', 'email', 'name', 'disabled', 'role',
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
    list_display_links= ['email',]
    list_editable = ['name', 'disabled', 'role', 'phone', 'subscribe_news', 'disabled_by', 'updated_by',]


class ProductAdmin(admin.ModelAdmin):
    def change_category_to_default(self, request, queryset):
        queryset.update(category="default")

    ordering = ['id']
    list_display = ['id', 'product_name', 'category', 'rating', 'price', 'discount','duration','created_by',
                    'sPrice','mPrice','lPrice',]
    search_fields = ['product_name', 'id', 'category',]
    actions = ['change_category_to_default',]
    list_editable = ['discount','rating','price','duration','sPrice','mPrice','lPrice',]
    list_filter = ['category', 'rating',]
    list_per_page = 50
    list_display_links= ['product_name',]


class NotificationAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ['subject', 'item_id', 'email']
    list_display = ['subject', 'item_id', 'email']
    list_filter = ['subject',]
    list_per_page = 50

class OrderAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'product_name','order_id','category','delivery_type','total','paid','assigned_to',
                    'delivery_status','quantity',]
    search_fields = ['product_name', 'id', 'order_id',]
    list_filter = ['product_name',]
    list_per_page = 50
    list_display_links= ['order_id',]


class TaskAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'created_by','created_for','deadline','subject','status','created_at']
    search_fields = ['created_by', 'id', 'created_for','status',]
    list_filter = ['created_by','status',]
    list_per_page = 50
    list_display_links = ['created_by',]




admin.site.unregister(Group)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Category)
admin.site.register(models.ContactUs)
admin.site.register(models.EmailMessage)
admin.site.register(models.EmailOtp)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Orders, OrderAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ResetPassword)
admin.site.register(models.Review)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.AuthToken)
admin.site.register(models.Transactions)
admin.site.register(models.Wishlist)
admin.site.register(models.AddOrderPendingEmail)
admin.site.register(models.AddPendingEmail2)
admin.site.register(models.AddPendingEmail)
admin.site.register(models.BillingDetails)
admin.site.register(models.Coupon)



