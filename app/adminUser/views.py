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
# class Update_delete(APIView):
#     renderer_classes = [JSONRenderer]
#     # delete item function
#     @staticmethod
#     def delete(request):
#         claims = check_http_auth(request)
#         set = ["user", "admin", "superAdmin", "rider"]

#         id = request.query_params.get('id', None)
#         tablename = request.query_params.get('tablename', None)

#         if id == None or id == "" or tablename == None or tablename == "":
#             msg = dict(error='Missing ID or tablename')
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
#                 tablenames = ["reviews", "billing", "wishlist"]
#                 if tablename not in tablenames:
#                     msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
#                     return Response(msg)
#                 else:
#                     if tablename == 'billing':
#                         if BillingDetails.objects.filter(pk=id, user=userD.id).exists():
#                             delete_item = BillingDetails.objects.get(pk=id, user=userD.id).delete()
#                             msg = dict(msg="Successfully Deleted!")
#                             return Response(msg)
#                         else:
#                             msg = dict(msg="Does not exist!")
#                             return Response(msg)
#                     elif tablename == "reviews":
#                         if Review.objects.filter(pk=id, created_by=userD.id).exists():
#                             delete_item = Review.objects.get(pk=id, created_by=userD.id).delete()
#                             msg = dict(msg="Successfully Deleted!")
#                             return Response(msg)
#                         else:
#                             msg = dict(msg="Does not exist!")
#                             return Response(msg)
#                     elif tablename == "wishlist":
#                         if Wishlist.objects.filter(pk=id, created_by=userD.id).exists():
#                             delete_item = Wishlist.objects.get(pk=id, created_by=userD.id).delete()
#                             msg = dict(msg="Successfully Deleted!")
#                             return Response(msg)
#                         else:
#                             msg = dict(msg="Does not exist!")
#                             return Response(msg)
#             except auth_user.DoesNotExist:
#                 msg = dict(error='Invalid User please Relogin!')
#                 return Response(msg)


#     # update item function
#     @staticmethod
#     def put(request):
#         claims = check_http_auth(request)
#         set = ["user", "admin", "superAdmin", "rider"]

#         id = request.query_params.get('id', None)
#         tablename = request.query_params.get('tablename', None)

#         if id == None or id == "" or tablename == None or tablename == "":
#             msg = dict(error='Missing ID or tablename')
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
#                 tablenames = ["reviews", "billing"]
#                 if tablename not in tablenames:
#                     msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
#                     return Response(msg)
#                 else:
#                     if tablename == 'billing':
#                         if BillingDetails.objects.filter(pk=id, user=userD.id).exists():
#                             address = json.loads(request.body).get('address', None)
#                             apartment = json.loads(request.body).get('apartment', None)
#                             notes = json.loads(request.body).get('notes', None)
#                             if address == None or address == "":
#                                 msg = dict(error='Missing ID or Address')
#                                 return Response(msg)
#                             BillingDetails.objects.filter(pk=id, user=userD.id).update(address=address,
#                                 apartment=apartment, notes=notes)
#                             msg = dict(msg="Successfully Updated!")
#                             return Response(msg)
#                         else:
#                             msg = dict(msg="Does not exist!")
#                             return Response(msg)
#                     elif tablename == "reviews":
#                         if Review.objects.filter(pk=id, created_by=userD.id).exists():
#                             rating_pro = json.loads(request.body).get('rating', None)
#                             description = json.loads(request.body).get('description', None)
#                             if rating_pro == None or rating_pro == "" or description == None \
#                                 or description == "":
#                                 msg = dict(error='Missing ID or rating or description')
#                                 return Response(msg)
#                             upd = Review.objects.filter(pk=id, created_by=userD.id).update(rating=rating_pro,
#                                 description=description)
#                             get_review = Review.objects.get(pk=upd)
#                             rating = Product.objects.get(pk=get_review.product_id.id)
#                             if rating_pro == 5:
#                                 rnd = round( (5*int(rating.rating5 + 1) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5 + 1)), 1)
#                                 upd2 = Product.objects.filter(pk=rating.id).update(
#                                     rating5=int(rating.rating5)+1, rating=rnd)
#                                 msg = dict(msg="Successfully Updated!")

#                             elif rating_pro == 4:
#                                 rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4 + 1)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4 + 1) + int(rating.rating5)), 1)
#                                 upd2 = Product.objects.filter(pk=rating.id).update(
#                                     rating5=int(rating.rating4)+1, rating=rnd)
#                                 msg = dict(msg="Successfully Updated!")

#                             elif rating_pro == 3:
#                                 rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3 + 1) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3 + 1) + int(rating.rating4) + int(rating.rating5)), 1)
#                                 upd2 = Product.objects.filter(pk=rating.id).update(
#                                     rating5=int(rating.rating3)+1, rating=rnd)
#                                 msg = dict(msg="Successfully Updated!")
                            
#                             elif rating_pro == 2:
#                                 rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2 + 1) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2 + 1)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5)), 1)
#                                 upd2 = Product.objects.filter(pk=rating.id).update(
#                                     rating5=int(rating.rating2)+1, rating=rnd)
#                                 msg = dict(msg="Successfully Updated!")
                            
#                             elif rating_pro == 1:
#                                 rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1 + 1)) / (int(rating.rating1 + 1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5)), 1)
#                                 upd2 = Product.objects.filter(pk=rating.id).update(
#                                     rating5=int(rating.rating1)+1, rating=rnd)
#                                 msg = dict(msg="Successfully Updated!")
#                             else:
#                                 msg = dict(msg="Invalid rating number, rating should be between 1-5!")
#                             return Response(msg)
#                         else:
#                             msg = dict(msg="Does not exist!")
#                             return Response(msg)
#             except auth_user.DoesNotExist:
#                 msg = dict(error='Invalid User please Relogin!')
#                 return Response(msg)




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