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
from core.models import Product, ContactUs, EmailOtp, Notification, Test, AuthToken, \
    Wishlist, BillingDetails, Orders, AddPendingEmail, SpecialOrder
from user.views import check_http_auth,  check_http_auth2, ValidatePhone, ResizeImage

auth_user = get_user_model()

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