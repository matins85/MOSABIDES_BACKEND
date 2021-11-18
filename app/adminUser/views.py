from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from rest_framework import generics
import os
import base64
import json
import requests
import concurrent.futures
import asyncio
from aiohttp import ClientSession
import string
import copy
import secrets
import random
import ast
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import phonenumbers
import random
from django.db.models import Q
from core.models import Product, ContactUs, EmailOtp, Notification, Test, AuthToken, Task, \
    Wishlist, BillingDetails, Orders, AddPendingEmail, SpecialOrder, Coupon, Review, Transactions
from user.views import check_http_auth,  check_http_auth2, ValidatePhone, ResizeImage, send_email, \
    get_random_alphanumeric_string

auth_user = get_user_model()

profile_image_size = 300
product_image_size = 600



# super admin add staff
class AddStaff(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["superAdmin"]

        email = request.query_params.get('email', None)

        if email == None or email == "":
            msg = dict(error='Missing user email')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                if not auth_user.objects.filter(email=email).exists():
                    msg = dict(error="User does not exist!")
                    return Response(msg)
                else:
                    if auth_user.objects.filter(email=email, role="admin").exists():
                        msg = dict(error='Already an Admin')
                        return Response(msg)
                    else:
                        saveC = auth_user.objects.filter(email=email).update(is_staff=True, role="admin")
                        msg = dict(msg='success')
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)



    # remove as admin
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["superAdmin"]

        email = request.query_params.get('email', None)

        if email == None or email == "":
            msg = dict(error='Missing user email')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                if not auth_user.objects.filter(email=email, role="admin").exists():
                    msg = dict(error="User is not an Admin!")
                    return Response(msg)
                else:
                    saveC = auth_user.objects.filter(email=email).update(is_staff=False, role="user")
                    msg = dict(msg='success')
                    return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)
    


# super admin add rider
class AddRider(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["superAdmin"]

        email = request.query_params.get('email', None)

        if email == None or email == "":
            msg = dict(error='Missing user email')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                if not auth_user.objects.filter(email=email).exists():
                    msg = dict(error="User does not exist!")
                    return Response(msg)
                else:
                    if auth_user.objects.filter(email=email, role="rider").exists():
                        msg = dict(error='Already a Rider')
                        return Response(msg)
                    else:
                        saveC = auth_user.objects.filter(email=email).update(is_staff=True, role="rider")
                        msg = dict(msg='success')
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


    # remove as rider
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["superAdmin"]

        email = request.query_params.get('email', None)

        if email == None or email == "":
            msg = dict(error='Missing user email')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                if not auth_user.objects.filter(email=email, role="rider").exists():
                    msg = dict(error="User is not a Rider!")
                    return Response(msg)
                else:
                    saveC = auth_user.objects.filter(email=email).update(is_staff=False, role="user")
                    msg = dict(msg='success')
                    return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)




# update and delete functions
class Update_delete(APIView):
    renderer_classes = [JSONRenderer]
    # delete item function
    @staticmethod
    def delete(request):
        claims = check_http_auth(request)
        set = ["admin", "superAdmin"]

        id = request.query_params.get('id', None)
        tablename = request.query_params.get('tablename', None)

        if id == None or id == "" or tablename == None or tablename == "":
            msg = dict(error='Missing ID or tablename')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                tablenames = ["reviews", "coupon", "product", "special_order", "contact_us", ]
                if tablename not in tablenames:
                    msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
                    return Response(msg)
                else:
                    if tablename == 'contact_us':
                        if ContactUs.objects.filter(pk=id).exists():
                            delete_item = ContactUs.objects.get(pk=id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    elif tablename == "reviews":
                        if Review.objects.filter(pk=id).exists():
                            delete_item = Review.objects.get(pk=id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    elif tablename == "special_order":
                        if SpecialOrder.objects.filter(pk=id).exists():
                            delete_item = SpecialOrder.objects.get(pk=id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    elif tablename == "product":
                        if Product.objects.filter(pk=id).exists():
                            delete_item = Product.objects.get(pk=id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    elif tablename == "coupon":
                        if Coupon.objects.filter(pk=id).exists():
                            delete_item = Coupon.objects.get(pk=id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


    # update item function
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["admin", "superAdmin"]

        id = request.query_params.get('id', None)
        tablename = request.query_params.get('tablename', None)

        if id == None or id == "" or tablename == None or tablename == "":
            msg = dict(error='Missing ID or tablename')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                tablenames = ["product", "user", "coupon"]
                if tablename not in tablenames:
                    msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
                    return Response(msg)
                else:
                    if tablename == 'product':
                        if Product.objects.filter(pk=id).exists():
                            product_name = json.loads(request.body).get('product_name', None)
                            category = json.loads(request.body).get('category', None)
                            description = json.loads(request.body).get('description', None)
                            discount = json.loads(request.body).get('discount', None)
                            image = json.loads(request.body).get('image', None)
                            sPrice = json.loads(request.body).get('sPrice', None)
                            mPrice = json.loads(request.body).get('mPrice', None)
                            lPrice = json.loads(request.body).get('lPrice', None)
                            sPrice_desc = json.loads(request.body).get('sPrice_desc', None)
                            mPrice_desc = json.loads(request.body).get('mPrice_desc', None)
                            lPrice_desc = json.loads(request.body).get('lPrice_desc', None)
                            duration = json.loads(request.body).get('duration', None)
                            if product_name == None or product_name == "" or category == None or category == "" \
                                or description == None or description == "" or discount == None or discount == "" \
                                or duration == None or duration == "":
                                msg = dict(error='Missing product_name or category or description or discount or duration')
                                return Response(msg)
                            get_product = Product.objects.get(pk=id)
                            Product.objects.filter(pk=id).update(product_name=product_name, mPrice=mPrice, lPrice=lPrice, discount=discount,
                                category=category, description=description, sPrice=sPrice, sPrice_desc=sPrice_desc, mPrice_desc=mPrice_desc,
                                lPrice_desc=lPrice_desc, duration=duration, image=ResizeImage(image, product_image_size) if image != "" else get_product.image)
                            Notification.objects.create(subject="Update product", item_id=get_product.pk,
                                email=userD.email, body=f"{userD.name} Updated a product",
                                edit_by=userD, name=userD.name).save()
                            msg = dict(msg="Successfully Updated!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    elif tablename == 'coupon':
                        if Coupon.objects.filter(pk=id).exists():
                            discount = json.loads(request.body).get('discount', None)
                            if discount == None or discount == "" or discount < 2:
                                msg = dict(error='Missing discount or invalid discount number')
                                return Response(msg)
                            Coupon.objects.filter(pk=id).update(discount=discount)
                            Notification.objects.create(subject="Coupon updated", item_id=id,
                                email=userD.email, body=f"{userD.name} Updated a Coupon",
                                edit_by=userD, name=userD.name).save()
                            msg = dict(msg="Successfully Updated!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    elif tablename == 'user':
                        if auth_user.objects.filter(pk=id).exists():
                            email = json.loads(request.body).get('email', None)
                            phone = ValidatePhone(json.loads(request.body).get('phone', None))
                            name = json.loads(request.body).get('name', None)
                            subscribe_news = json.loads(request.body).get('subscribe_news', None)
                            if email == None or email == "" or phone == None or phone == "" or name == None or name == "" \
                                or subscribe_news == None or subscribe_news == "":
                                msg = dict(error='Missing email or phone or name or subscribe_news')
                                return Response(msg)
                            auth_user.objects.filter(pk=id).update(email=email, phone=phone['msg'], name=name, subscribe_news=subscribe_news,
                                    updated_by=userD.id)
                            Notification.objects.create(subject="Customer updated", item_id=id,
                                email=userD.email, body=f"{userD.name} Updated a Customer",
                                edit_by=userD, name=userD.name).save()
                            msg = dict(msg="Successfully Updated!")
                            return Response(msg)
                        else:
                            msg = dict(error="Does not exist!")
                            return Response(msg)
                    
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)




# get data by tablename functions
class ALL_ITEM(APIView):
    renderer_classes = [JSONRenderer]

    @staticmethod
    def get(request):
        claims = check_http_auth2(request)
        set = ["admin", "superAdmin"]
        tablename = request.query_params.get('tablename', None)
    
        tablenames = ["orders", "products", "contact_us", "notifications", "special_orders", "customers", 
            "tasks", "coupon", "reviews", "transactions"]

        if tablename == None or tablename == "":
            msg = dict(error=f"Missing tablename: avaliable tablenames {tablenames}")
            return Response(msg)
        else:
            if tablename not in tablenames:
                msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
                return Response(msg)
            else:
                
                # Products
                if tablename == 'products':
                    list_all = Product.objects.values('product_name', 'description', 'category', 'price', 
                        'discount', 'rating', 'rating1', 'rating2', 'rating3', 'rating4', 'rating5',
                        'seen', 'purchase', 'image', 'sPrice', 'mPrice', 'lPrice',
                        'sPrice_desc', 'mPrice_desc', 'lPrice_desc', 'duration', 'created_by')
                    msg = dict(msg=list_all)
                    return Response(msg)
                
                # coupon
                elif tablename == 'coupon':
                    list_all = Coupon.objects.values('coupon', 'discount', 'used', 'seen', 
                                'created_at', 'created_for', 'email')
                    msg = dict(msg=list_all)
                    return Response(msg)
                
                # review
                elif tablename == 'reviews':
                    list_all = Review.objects.values('rating', 'description', 'name', 'email',
                                'seen', 'product_id', 'created_at', 'created_by')
                    msg = dict(msg=list_all)
                    return Response(msg)

                # Customers
                elif tablename == 'customers':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = auth_user.objects.values('id', 'email', 'name', 'role', 'phone',
                                'subscribe_news', 'image', 'last_login', 'is_staff', 'disabled', 'disabled_by',
                                'updated_by', 'created_at')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)

                # Contact us
                elif tablename == 'contact_us':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = ContactUs.objects.values('name', 'email', 'subject', 'description', 
                                'seen', 'total', 'paid', 'delivery_fee', 'image', 'reference', 'price_desc',
                                'seen', 'created_at', 'created_by')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)

                # Notification
                elif tablename == 'notifications':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = Notification.objects.values('name', 'email', 'subject', 'item_id', 
                        'body', 'edit_by', 'created_at')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)

                # Special order
                elif tablename == 'special_orders':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = SpecialOrder.objects.values('image', 'description', 'name', 'email', 
                        'quantity', 'seen', 'created_at', 'created_by')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)
                
                # order
                elif tablename == 'orders':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = Orders.objects.values('product_name', 'delivery_type', 'category', 'price', 
                        'order_id', 'total', 'paid', 'delivery_fee', 'image', 'reference', 'price_desc',
                        'seen', 'duration', 'product_id', 'billing_id', 'delivery_status', 'assigned_to',
                        'top_up', 'quantity', 'paid_status', 'created_by', 'created_at')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)

                # Task
                elif tablename == 'tasks':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = Task.objects.values('created_by', 'created_at', 'deadline', 'subject', 
                        'status', 'seen', 'description')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)


                # transactions
                elif tablename == 'transactions':
                    if claims == None:
                        msg = dict(error='Authorization header not supplied.')
                        return Response(msg)
                    elif claims.get('error', None) != None:
                        return Response(claims)
                    try:
                        userD = auth_user.objects.get(pk=claims["msg"]["id"])
                        if userD.role not in set:
                            msg = dict(error="Unauthorized Request.")
                            return Response(msg)
                        else:
                            list_all = Transactions.objects.values('product_name', 'order_id', 'total', 'seen', 
                                'pay_type', 'reference', 'channel', 'brand', 'created_at', 'status')
                            msg = dict(msg=list_all)
                            return Response(msg)
                    except auth_user.DoesNotExist:
                        msg = dict(error="Unauthorized Request.")
                        return Response(msg)



# enable and disable user class
class AdminEnaDisUser(APIView):
    renderer_classes = [JSONRenderer]
    # enable and disable user function
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["superAdmin", "admin"]

        id = request.query_params.get('id', None)
        user_type = request.query_params.get('type', None)

        if id == None or id == "" or user_type == None or user_type == "":
            msg = dict(error='Missing user type or ID')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                if user_type == "disable":
                    if (userD.role == "admin") and (auth_user.objects.filter(pk=id, role="superAdmin", is_staff=True).exists()):
                        msg = dict(error="Cannot disable SuperAdmin!")
                        return Response(msg)
                    elif (userD.role == "admin") and (auth_user.objects.filter(Q(pk=id) & Q(role="admin") & Q(is_staff=True)).exists()):
                        msg = dict(error="Cannot disable another Admin!")
                        return Response(msg)
                    elif (userD.role == "superAdmin") and (auth_user.objects.filter(pk=id, role="superAdmin", is_staff=True).exists()):
                        msg = dict(error="Cannot disable SuperAdmin!")
                        return Response(msg)
                    elif (userD.role == "superAdmin") and (auth_user.objects.filter(Q(pk=id) & Q(role="admin") & Q(is_staff=True) & Q(disabled=False)).exists()):
                        auth_user.objects.filter(pk=id).update(disabled=True, disabled_by=userD.id)
                        Notification.objects.create(subject="Account Disabled", item_id=id, email=userD.email, 
                            body=f"{userD.name} Disabled an Account", edit_by=userD, name=userD.name).save()
                        msg = dict(msg="Success")
                        return Response(msg)
                    elif (userD.role == "superAdmin") and (auth_user.objects.filter(Q(pk=id) & Q(role="user") & Q(is_staff=False) & Q(disabled=False)).exists()):
                        auth_user.objects.filter(pk=id).update(disabled=True, disabled_by=userD.id)
                        Notification.objects.create(subject="Account Disabled", item_id=id, email=userD.email, 
                            body=f"{userD.name} Disabled an Account", edit_by=userD, name=userD.name).save()
                        msg = dict(msg="Success")
                        return Response(msg)
                    elif (userD.role == "admin") and (auth_user.objects.filter(Q(pk=id) & Q(role="user") & Q(is_staff=False) & Q(disabled=False)).exists()):
                        auth_user.objects.filter(pk=id).update(disabled=True, disabled_by=userD.id)
                        Notification.objects.create(subject="Account Disabled", item_id=id, email=userD.email, 
                            body=f"{userD.name} Disabled an Account", edit_by=userD, name=userD.name).save()
                        msg = dict(msg="Success")
                        return Response(msg)
                    else:
                        msg = dict(msg="Already Disabled")
                        return Response(msg)
                elif user_type == "enable":
                    auth_user.objects.filter(pk=id).update(disabled=False, disabled_by=None)
                    Notification.objects.create(subject="Account Enabled", item_id=id, email=userD.email, 
                            body=f"{userD.name} Enabled an Account", edit_by=userD, name=userD.name).save()
                    msg = dict(msg="Success")
                    return Response(msg)
                else:
                    msg = dict(error='Invalid Type, should be either enable or disable')
                    return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)



# update seen class
class Viewed(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["superAdmin", "admin"]

        id = request.query_params.get('id', None)
        tablename = request.query_params.get('tablename', None)

        if id == None or id == "" or tablename == None or tablename == "":
            msg = dict(error='Missing tablename or ID')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                tablenames = ["product", "user", "contact_us", "special_order", "order_purchase", "task", "coupon"]
                if tablename not in tablenames:
                    msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
                    return Response(msg)
                else:
                    if tablename == "product":
                        Product.objects.filter(pk=id).update(seen=True)
                    elif tablename == "user":
                        auth_user.objects.filter(pk=id).update(seen=True)
                    elif tablename == "contact_us":
                        ContactUs.objects.filter(pk=id).update(seen=True)
                    elif tablename == "special_order":
                        SpecialOrder.objects.filter(pk=id).update(seen=True)
                    elif tablename == "order_purchase":
                        Orders.objects.filter(order_id=id).update(seen=True)
                    elif tablename == "task":
                        Task.objects.filter(pk=id).update(seen=True)
                    elif tablename == "coupon":
                        Coupon.objects.filter(pk=id).update(seen=True)
                    return Response({"msg": "success"})
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


# special order class
# class AddspecialOrder(APIView):
#     renderer_classes = [JSONRenderer]
#     @staticmethod
#     def post(request):
#         claims = check_http_auth(request)
#         set = ["superAdmin", "admin"]

#         id = request.query_params.get('id', None)
#         orders = json.loads(request.body)

#         if orders == None or orders == "" or id == None or id == "":
#             msg = dict(error='Missing order details or ID')
#             return Response(msg)
#         if claims == None:
#             msg = dict(error='Authorization header not supplied.')
#             return Response(msg)
#         elif claims.get('error', None) != None:
#             return Response(claims)
#         else:
#             try:
#                 userD = auth_user.objects.get(pk=claims["msg"]["id"])
#                 if userD.role not in set:
#                     msg = dict(error="Unauthorized Request.")
#                     return Response(msg)
#                 else:
#                     if auth_user.objects.filter(pk=id).exists():
#                         res = get_random_numeric_string(10)
#                         copy_res = f"MOB{copy.copy(res)}"
#                         if Orders.objects.filter(order_id=copy_res).exists():
#                             OrderPurchase().post(request)
#                         else:
#                             rows2 = json.loads(request.body)[0]
#                             customer = auth_user.objects.get(pk=id)

#                             for row in orders:
#                                 upd = row.update({"order_id": copy_res})
#                                 upd2 = row.update({"created_by": customer.id})
#                                 upd3 = row.update({"billing_id": billing_id.id})
#                             save_list = [Orders(product_id=Product.objects.get(pk=row["product_id"]), product_name=row["product_name"],
#                                 billing_id=BillingDetails.objects.get(pk=row["billing_id"]), delivery_type=row["delivery_type"],
#                                 category=row["category"], price=row["price"], order_id=row["order_id"], duration=row["duration"],
#                                 paid=row["paid"], reference=row["reference"], total=row["total"], delivery_fee=row["delivery_fee"],
#                                 price_desc=row["price_desc"], top_up=row["top_up"], quantity=row["quantity"],
#                                 created_by=customer,
#                             ) for row in orders]
#                             save = Orders.objects.bulk_create(save_list)
#                             find_save_data = Orders.objects.filter(order_id=copy_res)[0]
#                             # save_trans = Transactions.objects.create(product_name=find_save_data.product_name,
#                             #     order_id=find_save_data.order_id, total=find_save_data.total, 
#                             #     reference=find_save_data.reference, pay_type=rows2["pay_type"].lower()).save()
#                             upd_email = AddOrderPendingEmail.objects.create(
#                                 email=userD.email, order_id=copy_res, reference=find_save_data.reference).save()
#                             # add_notify = Notification.objects.create(subject="Order", item_id=copy_res, 
#                             #     email=userD.email, body=f"{userD.name} Purchase an order with Order ID: {copy_res}", edit_by=userD, 
#                             #     name=userD.name).save()
#                             # userD.purchase = userD.purchase + len(orders)
#                             # userD.save()
#                             # pro = Orders.objects.filter(order_id=copy_res)
#                             # for id in pro:
#                             #     updPro = Product.objects.filter(pk=id.product_id.pk)
#                             #     save_purchase = [updPro.update(purchase=int(sv.purchase) + 1) for sv in updPro]
#                             # msg = Return_profile_details(userD)
#                             return Response(msg)
#                     else:
#                         msg = dict(error='Invalid Customer!')
#                         return Response(msg)
#             except auth_user.DoesNotExist:
#                 msg = dict(error='Invalid User please Relogin!')
#                 return Response(msg)



# special order class
class GenerateCoupon(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["superAdmin", "admin"]

        id = request.query_params.get('id', None)
        discount = request.query_params.get('discount', None)

        if discount == None or discount == "" or id == None or id == "":
            msg = dict(error='Missing discount or ID')
            return Response(msg)
        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                else:
                    if not Coupon.objects.filter(created_for=id, used=False).exists():
                        coupon = get_random_alphanumeric_string(10)
                        copy_coup = copy.copy(coupon)
                        user = auth_user.objects.get(pk=id)
                        context = dict(coupon=copy_coup, type="generate", discount=discount)
                        sendcode2 = send_email(user.email, 'Congratulations', 'coupon', context)
                        if sendcode2["msg"] == "success":
                            save = Coupon.objects.create(coupon=copy_coup, discount=discount, 
                            email=user.email, created_for=user).save()
                            msg = dict(msg="success")
                            return Response(msg)
                        else:
                            msg = dict(error='An error occur, please try again!')
                            return Response(msg)
                    else:
                        msg = dict(error="Cannot Gift coupon because this user has not used the previous one")
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)