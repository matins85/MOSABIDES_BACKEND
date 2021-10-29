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
    Wishlist, BillingDetails, Orders, AddPendingEmail, SpecialOrder, Coupon, Review, Transactions, \
    AddOrderPendingEmail, Category
from user.views import check_http_auth,  check_http_auth2, ValidatePhone, ResizeImage, get_random_numeric_string

auth_user = get_user_model()



def Return_profile_details(userD):
    # userD = auth_user.objects.get(pk=id)
    # profile
    profile = {
        'id': userD.id, 'email': userD.email, 'name': userD.name,
        'role': userD.role, 'phone': userD.phone, 'subscribe_news': userD.subscribe_news,
        'purchase': userD.purchase, 'seen': userD.seen, 'image': userD.image,
        'last_login': userD.last_login, 'is_staff': userD.is_staff, 'updated_by': userD.updated_by,
        'disabled': userD.disabled, 'disabled_by': userD.disabled_by, 'created_at': userD.created_at
    }
    # billing
    billings = BillingDetails.objects.filter(user=userD.id)
    billing = [{'user': bill.user.id, 'address': bill.address, 'apartment': bill.apartment,
            'notes': bill.notes, 'id': bill.pk
        } for bill in billings]
    # wishlist
    wishlists = Wishlist.objects.filter(created_by=userD.id)
    wishlist = [{'id': wish.pk, 'product_id': wish.product_id.id, 'product_name': wish.product_id.product_name,
            'duration': wish.product_id.duration, 'wishlist_created_by': wish.created_by.id,
            'discount': wish.product_id.discount, 'category': wish.product_id.category.id,
            'price': wish.product_id.price, 'rating': wish.product_id.rating, 'purchase': wish.product_id.purchase,
            'description': wish.product_id.description, 'sPrice': wish.product_id.sPrice, 'image': wish.product_id.image,
            'mPrice': wish.product_id.mPrice, 'lPrice': wish.product_id.lPrice, 'seen': wish.product_id.seen,
            'sPrice_desc': wish.product_id.sPrice_desc, 'mPrice_desc': wish.product_id.mPrice_desc,
            'lPrice_desc': wish.product_id.lPrice_desc, 'wishlist_created_at': wish.created_at
        } for wish in wishlists]
    # Orders
    orders = Orders.objects.filter(created_by=userD.id)
    order = [{'id': od.pk, 'product_id': od.product_id.id, 'product_name': od.product_name,
            'billing_id': od.billing_id.id,
            'delivery_type': od.delivery_type, 'category': od.category,
            'price': od.price, 'order_id': od.order_id, 'paid': od.paid, 'image': od.product_id.image,
            'reference': od.reference, 'price_desc': od.price_desc, 'seen': od.seen,
            'delivery_status': od.delivery_status, 'top_up': od.top_up, 'quantity': od.quantity, 
            'paid_status': od.paid_status, 'created_at': od.created_at,
            'created_by': od.created_by.id} for od in orders]
    orders2 = Orders.objects.filter(created_by=userD.id)[0]
    order_billing = {'email': orders2.billing_id.user.email, 'address': orders2.billing_id.address,
                'rider_name': orders2.assigned_to.name, 'rider_phone': orders2.assigned_to.phone,
                'apartment': orders2.billing_id.apartment, 'notes': orders2.billing_id.notes,
                'name': orders2.billing_id.user.name, 'phone': orders2.billing_id.user.phone,
                'total': orders2.total, 'delivery_fee': orders2.delivery_fee, 'duration': orders2.duration}
    return dict(profile=profile, billing=billing, wishlist=wishlist, 
        order=dict(order=order, billing_user=order_billing))



class Contact_Us(APIView):
    renderer_classes = [JSONRenderer]
    # email the admin
    @staticmethod
    def post(request):
        claims = check_http_auth2(request)
        set = ["user", "admin", "superAdmin", "rider"]

        name = json.loads(request.body).get('name', None)
        email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
        subject = json.loads(request.body).get('subject', None)
        description = json.loads(request.body).get('description', None)

        if email == None or email == "" or name == None or name == "" \
            or description == None or description == "" or subject == None or subject == "":
            msg = dict(error='Missing email or name or description or subject')
            return Response(msg)

        if claims == None:
            if ContactUs.objects.filter(email=email, name=name, description=description, subject=subject).exists():
                msg = dict(error="Already exists")
                return Response(msg)
            else:
                saveC = ContactUs.objects.create(name=name, email=email, description=description, 
                    subject=subject)
                saveC.save()
                if saveC:
                    save = ContactUs.objects.get(pk=saveC.id)
                    add_notify = Notification.objects.create(subject="Connect", item_id=save.id, email=save.email, body=f"{save.name} wants to connect about {save.subject}", name=save.name).save()
                    msg = dict(msg='success')
                    return Response(msg)

        elif claims.get('error', None) != None:
            return Response(claims)
        else:
            try:
                userD = auth_user.objects.get(pk=claims["msg"]["id"])
                if userD.role not in set:
                    msg = dict(error="Unauthorized Request.")
                    return Response(msg)
                if ContactUs.objects.filter(email=email, name=name, description=description, subject=subject).exists():
                    msg = dict(error="Already exists")
                    return Response(msg)
                else:
                    saveC = ContactUs.objects.create(name=name, email=email, description=description, 
                        subject=subject, created_by=userD, image=ResizeImage(image, 300) if image != "" else None)
                    saveC.save()
                    if saveC:
                        save = ContactUs.objects.get(pk=saveC.id)
                        add_notify = Notification.objects.create(subject="Connect", item_id=save.id, email=save.email, body=f"{save.name} wants to connect about {save.subject}",
                            edit_by=userD, name=save.name).save()
                        msg = dict(msg='success')
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


# # user request special order
class Special_order(APIView):
    renderer_classes = [JSONRenderer]
    # user request special order
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        image = json.loads(request.body).get('image', None)
        quantity = json.loads(request.body).get('quantity', None)
        description = json.loads(request.body).get('description', None)

        if image == None or image == "" or quantity == None or quantity == "" \
            or description == None or description == "":
                msg = dict(error='Missing image or description or quantity')
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
                if SpecialOrder.objects.filter(email=userD.email, quantity=quantity, description=description).exists():
                    msg = dict(error="Already exists")
                    return Response(msg)
                else:
                    saveC = SpecialOrder.objects.create(name=userD.name, email=userD.email, description=description, 
                        quantity=quantity, created_by=userD, image=ResizeImage(image, 600) if image != "" else None)
                    saveC.save()
                    if saveC:
                        save = SpecialOrder.objects.get(pk=saveC.id)
                        add_notify = Notification.objects.create(subject="Special Order", item_id=save.id, email=save.email, body=f"{save.email} Request a special order",
                            edit_by=userD, name=save.name).save()
                        msg = dict(msg='success')
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)



# user add product to their wishlist
class AddWishlist(APIView):
    renderer_classes = [JSONRenderer]
    # user request special order
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        product_id = request.query_params.get('product_id', None)

        if product_id == None or product_id == "":
            msg = dict(error='Missing product ID')
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
                if not Product.objects.filter(pk=product_id).exists():
                    msg = dict(error="Food Item does not exist!")
                    return Response(msg)
                else:
                    if Wishlist.objects.filter(product_id=product_id, created_by=userD.id).exists():
                        msg = dict(msg='Already exists')
                        return Response(msg)
                    else:
                        saveC = Wishlist.objects.create(product_id=Product.objects.get(pk=product_id), created_by=userD)
                        saveC.save()
                        if saveC:
                            msg = Return_profile_details(userD)
                            return Response(msg)
                        else:
                            msg = dict(msg='Cannot save to wishlist')
                            return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)




class Billing(APIView):
    renderer_classes = [JSONRenderer]
    # user request special order
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        address = json.loads(request.body).get('address', None)
        apartment = json.loads(request.body).get('apartment', None)
        notes = json.loads(request.body).get('notes', None)

        if address == None or address == "":
            msg = dict(error='Missing Address')
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
                if BillingDetails.objects.filter(user=userD).exists():
                    msg = dict(error="Cannot add more than one address")
                    return Response(msg)
                else:
                    saveC = BillingDetails.objects.create(user=userD, address=address, apartment=apartment, notes=notes)
                    saveC.save()
                    if saveC:
                        msg = dict(msg=saveC.id)
                        return Response(msg)
                    else:
                        msg = dict(msg='Cannot save Address details')
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


    # update billing details
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        id = json.loads(request.body).get('id', None)
        address = json.loads(request.body).get('address', None)
        apartment = json.loads(request.body).get('apartment', None)
        notes = json.loads(request.body).get('notes', None)

        if address == None or address == "":
            msg = dict(error='Missing Address')
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
                if not BillingDetails.objects.filter(pk=id, user=userD.id).exists():
                    msg = dict(error="Does not exists")
                    return Response(msg)
                else:
                    saveC = BillingDetails.objects.filter(pk=id, user=userD.id).update(address=address, apartment=apartment, notes=notes)
                    msg = Return_profile_details(userD)
                    return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)



# update and delete functions
class AddRewview(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        product_id = json.loads(request.body).get('product_id', None)
        rating_pro = json.loads(request.body).get('rating', None)
        description = json.loads(request.body).get('description', None)

        if product_id == None or product_id == "" or rating_pro == None or rating_pro == "" \
            or description == None or description == "":
            msg = dict(error='Missing product_id or rating or description')
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
                if not Orders.objects.filter(created_by=userD.id, product_id=product_id, paid=True).exists():
                    if not Review.objects.filter(product_id=product_id, created_by=userD.id).exists():
                        rating = Product.objects.get(pk=product_id)
                        regis = Review.objects.create(rating=rating_pro, description=description, name=userD.name,
                            email=userD.email, product_id=rating, created_by=userD).save()
                        if rating_pro == 5:
                            rnd = round( (5*int(rating.rating5 + 1) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5 + 1)), 1)
                            upd2 = Product.objects.filter(pk=rating.id).update(
                                rating5=int(rating.rating5)+1, rating=rnd)
                            msg = dict(msg="success")

                        elif rating_pro == 4:
                            rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4 + 1)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4 + 1) + int(rating.rating5)), 1)
                            upd2 = Product.objects.filter(pk=rating.id).update(
                                rating5=int(rating.rating4)+1, rating=rnd)
                            msg = dict(msg="success")

                        elif rating_pro == 3:
                            rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3 + 1) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3 + 1) + int(rating.rating4) + int(rating.rating5)), 1)
                            upd2 = Product.objects.filter(pk=rating.id).update(
                                rating5=int(rating.rating3)+1, rating=rnd)
                            msg = dict(msg="success")
                        
                        elif rating_pro == 2:
                            rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2 + 1) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2 + 1)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5)), 1)
                            upd2 = Product.objects.filter(pk=rating.id).update(
                                rating5=int(rating.rating2)+1, rating=rnd)
                            msg = dict(msg="success")
                        
                        elif rating_pro == 1:
                            rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1 + 1)) / (int(rating.rating1 + 1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5)), 1)
                            upd2 = Product.objects.filter(pk=rating.id).update(
                                rating5=int(rating.rating1)+1, rating=rnd)
                            msg = dict(msg="success")
                        else:
                            msg = dict(msg="Invalid rating, rating should be between 1-5!")
                        return Response(msg)
                    else:
                        msg = dict(msg="Already exist!")
                        return Response(msg)
                else:
                    msg = dict(msg="Cannot add your review because you've not purchased this Food!")
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
        set = ["user", "admin", "superAdmin", "rider"]

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
                tablenames = ["reviews", "billing", "wishlist"]
                if tablename not in tablenames:
                    msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
                    return Response(msg)
                else:
                    if tablename == 'billing':
                        if BillingDetails.objects.filter(pk=id, user=userD.id).exists():
                            delete_item = BillingDetails.objects.get(pk=id, user=userD.id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(msg="Does not exist!")
                            return Response(msg)
                    elif tablename == "reviews":
                        if Review.objects.filter(pk=id, created_by=userD.id).exists():
                            delete_item = Review.objects.get(pk=id, created_by=userD.id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(msg="Does not exist!")
                            return Response(msg)
                    elif tablename == "wishlist":
                        if Wishlist.objects.filter(pk=id, created_by=userD.id).exists():
                            delete_item = Wishlist.objects.get(pk=id, created_by=userD.id).delete()
                            msg = dict(msg="Successfully Deleted!")
                            return Response(msg)
                        else:
                            msg = dict(msg="Does not exist!")
                            return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


    # update item function
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

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
                tablenames = ["reviews", "billing"]
                if tablename not in tablenames:
                    msg = dict(error=f"Invalid tablenames: avaliable tablenames {tablenames}")
                    return Response(msg)
                else:
                    if tablename == 'billing':
                        if BillingDetails.objects.filter(pk=id, user=userD.id).exists():
                            address = json.loads(request.body).get('address', None)
                            apartment = json.loads(request.body).get('apartment', None)
                            notes = json.loads(request.body).get('notes', None)
                            if address == None or address == "":
                                msg = dict(error='Missing ID or Address')
                                return Response(msg)
                            BillingDetails.objects.filter(pk=id, user=userD.id).update(address=address,
                                apartment=apartment, notes=notes)
                            msg = dict(msg="Successfully Updated!")
                            return Response(msg)
                        else:
                            msg = dict(msg="Does not exist!")
                            return Response(msg)
                    elif tablename == "reviews":
                        if Review.objects.filter(pk=id, created_by=userD.id).exists():
                            rating_pro = json.loads(request.body).get('rating', None)
                            description = json.loads(request.body).get('description', None)
                            if rating_pro == None or rating_pro == "" or description == None \
                                or description == "":
                                msg = dict(error='Missing ID or rating or description')
                                return Response(msg)
                            upd = Review.objects.filter(pk=id, created_by=userD.id).update(rating=rating_pro,
                                description=description)
                            get_review = Review.objects.get(pk=upd)
                            rating = Product.objects.get(pk=get_review.product_id.id)
                            if rating_pro == 5:
                                rnd = round( (5*int(rating.rating5 + 1) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5 + 1)), 1)
                                upd2 = Product.objects.filter(pk=rating.id).update(
                                    rating5=int(rating.rating5)+1, rating=rnd)
                                msg = dict(msg="Successfully Updated!")

                            elif rating_pro == 4:
                                rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4 + 1)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4 + 1) + int(rating.rating5)), 1)
                                upd2 = Product.objects.filter(pk=rating.id).update(
                                    rating5=int(rating.rating4)+1, rating=rnd)
                                msg = dict(msg="Successfully Updated!")

                            elif rating_pro == 3:
                                rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3 + 1) + 2*int(rating.rating2) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2)+ int(rating.rating3 + 1) + int(rating.rating4) + int(rating.rating5)), 1)
                                upd2 = Product.objects.filter(pk=rating.id).update(
                                    rating5=int(rating.rating3)+1, rating=rnd)
                                msg = dict(msg="Successfully Updated!")
                            
                            elif rating_pro == 2:
                                rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2 + 1) + 1*int(rating.rating1)) / (int(rating.rating1) + int(rating.rating2 + 1)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5)), 1)
                                upd2 = Product.objects.filter(pk=rating.id).update(
                                    rating5=int(rating.rating2)+1, rating=rnd)
                                msg = dict(msg="Successfully Updated!")
                            
                            elif rating_pro == 1:
                                rnd = round( (5*int(rating.rating5) + 4*int(rating.rating4)+ 3*int(rating.rating3) + 2*int(rating.rating2) + 1*int(rating.rating1 + 1)) / (int(rating.rating1 + 1) + int(rating.rating2)+ int(rating.rating3) + int(rating.rating4) + int(rating.rating5)), 1)
                                upd2 = Product.objects.filter(pk=rating.id).update(
                                    rating5=int(rating.rating1)+1, rating=rnd)
                                msg = dict(msg="Successfully Updated!")
                            else:
                                msg = dict(msg="Invalid rating number, rating should be between 1-5!")
                            return Response(msg)
                        else:
                            msg = dict(msg="Does not exist!")
                            return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)




# user purchase order
class OrderPurchase(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def get(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        order_id = request.query_params.get('order_id', None)

        if order_id == None or order_id == "":
            msg = dict(error='Missing order_id')
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
                if not Orders.objects.filter(order_id=order_id, created_by=userD.id).exists():
                    msg = dict(error="Order Does not exist!")
                    return Response(msg)
                else:
                    orders = Orders.objects.filter(order_id=order_id)
                    order = [{'id': od.pk, 'product_id': od.product_id.id, 'product_name': od.product_name,
                            'billing_id': od.billing_id.id,
                            'delivery_type': od.delivery_type, 'category': od.category.id,
                            'price': od.price, 'order_id': od.order_id, 'paid': od.paid, 'image': od.image,
                            'reference': od.reference, 'price_desc': od.price_desc, 'seen': od.seen,
                            'delivery_status': od.delivery_status, 'top_up': od.top_up,
                            'quantity': od.quantity, 'paid_status': od.paid_status, 'created_at': od.created_at,
                            'created_by': od.created_by.id} for od in orders]
                    orders2 = Orders.objects.filter(created_by=userD.id)[0]
                    order_billing = {'email': orders2.billing_id.user.email, 'address': orders2.billing_id.address,
                                'apartment': orders2.billing_id.apartment, 'notes': orders2.billing_id.notes,
                                'rider_name': od.assigned_to.name, 'rider_phone': od.assigned_to.phone,
                                'name': orders2.billing_id.user.name, 'phone': orders2.billing_id.user.phone,
                                'total': orders2.total, 'delivery_fee': orders2.delivery_fee, 'duration': orders2.duration}
                    msg = dict(order=order, billing_user=order_billing)
                    return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)


    # purchase order
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        rows = json.loads(request.body)
        rows2 = json.loads(request.body)[0]

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
                    res = get_random_numeric_string(10)
                    copy_res = f"MOB{copy.copy(res)}"
                    if Orders.objects.filter(order_id=copy_res).exists():
                        OrderPurchase().post(request)
                    else:
                        for row in rows:
                            upd = row.update({"order_id": copy_res})
                            upd2 = row.update({"created_by": userD.id})
                        save_list = [Orders(product_id=Product.objects.get(pk=row["product_id"]), product_name=row["product_name"],
                            billing_id=BillingDetails.objects.get(pk=row["billing_id"]), delivery_type=row["delivery_type"],
                            category=row["category"], price=row["price"], order_id=row["order_id"], duration=row["duration"],
                            paid=row["paid"], reference=row["reference"], total=row["total"], delivery_fee=row["delivery_fee"],
                            price_desc=row["price_desc"], top_up=row["top_up"], quantity=row["quantity"],
                            created_by=auth_user.objects.get(pk=row["created_by"]),
                        ) for row in rows]
                        save = Orders.objects.bulk_create(save_list)
                        find_save_data = Orders.objects.filter(order_id=copy_res)[0]
                        save_trans = Transactions.objects.create(product_name=find_save_data.product_name,
                            order_id=find_save_data.order_id, total=find_save_data.total, 
                            reference=find_save_data.reference, pay_type=rows2["pay_type"].lower()).save()
                        upd_email = AddOrderPendingEmail.objects.create(
                            email=userD.email, order_id=copy_res, reference=find_save_data.reference).save()
                        add_notify = Notification.objects.create(subject="Order", item_id=copy_res, 
                            email=userD.email, body=f"{userD.name} Purchase an order with Order ID: {copy_res}", edit_by=userD, 
                            name=userD.name).save()
                        userD.purchase = userD.purchase + 1
                        userD.save()
                        pro = Orders.objects.filter(order_id=copy_res)
                        for id in pro:
                            updPro = Product.objects.get(pk=id.product_id.pk)
                            updPro.purchase = int(updPro.purchase) + 1
                            updPro.save()
                        msg = Return_profile_details(userD)
                        return Response(msg)
            except auth_user.DoesNotExist:
                msg = dict(error='Invalid User please Relogin!')
                return Response(msg)