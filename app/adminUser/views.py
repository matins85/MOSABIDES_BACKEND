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
from user.views import check_http_auth,  check_http_auth2, ValidatePhone, ResizeImage

auth_user = get_user_model()




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
                        return R