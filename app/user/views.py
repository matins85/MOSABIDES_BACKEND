from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from rest_framework import generics
from django.core import serializers
import time
from datetime import datetime, timedelta
import os
import base64
import json
import requests
import concurrent.futures
import asyncio
from aiohttp import ClientSession
import string
import jwt
import copy
import secrets
import random
from PIL import Image
from werkzeug.utils import secure_filename
from io import StringIO, BytesIO
import hashlib
import ast
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import phonenumbers
from cryptography.fernet import Fernet
# from passlib.hash import pbkdf2_sha256
import random
from django.db.models import Q
from core.models import Product, ContactUs, EmailOtp, Notification, Test, AuthToken, \
    Wishlist, BillingDetails, Orders, AddPendingEmail


# special order resize size 
    # profile = 300,  special_order = 600

now = datetime.now()
# jwt secret key
super_secret_key = os.getenv('JWT')
# user model function
auth_user = get_user_model()
# server email sender email
EMAIL_SENDER = os.getenv('EMAIL_HOST_USER')
# salt for password hashing
# salt = bytes(os.getenv('SALT'), encoding='utf8')
# refresh token exp time
refresh_exp = 60*24
# acces token expire time
access_exp = 60


# generate random characters
def secure_rand(len=10):
    token=os.urandom(len)
    return base64.b64encode(token)


# generate number and alphabet string
def get_random_alphanumeric_string(length):
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters_and_digits = letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


# generate random number string
def get_random_numeric_string(length):
    letters_and_digits = string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


# hash password function 
def hash_password(password):
    # key = hashlib.pbkdf2_hmac(
    #     'sha256',
    #     password.encode('utf-8'),
    #     bytes(os.getenv('SALT'), encoding='utf8'),
    #     100000,
    #     dklen=30
    # )
    key = os.getenv('SALT2')
    f = Fernet(key)
    token = f.encrypt(bytes(password, encoding='utf8'))
    return str(token.decode())


# decrypt password function 
def decrypt_password(password):
    key = os.getenv('SALT2')
    f = Fernet(key)
    token = f.decrypt(bytes(bytes(password, encoding='utf8'))).decode()
    return str(token)



# validate phone number
def ValidatePhone(phone):
    if bool(phone) == True:
        my_number = phonenumbers.parse(phone, "NG")
        if phonenumbers.is_valid_number(my_number) == True:
            return dict(msg=phone)
        else:
            return dict(msg="error")
    else:
        return dict(msg="error")


# send email function
def send_email(to, subject, html, context):
    try:
        html_content = render_to_string('demo/{}.html'.format(html), context)
        msg = EmailMultiAlternatives(subject, '', EMAIL_SENDER, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return dict(msg='success')
    except Exception as e:
        return dict(msg='error')


# get base64 image, rename it, resize it and base64 encode
def encode_image(filename):
    # 1, file read
    ext = filename.split(".")[-1]
    with open(filename, "rb") as f:
        img = f.read()
    # 2, base64 encoded
    data = base64.b64encode(img).decode()
    # 3, the picture encoding string concatenation
    src = "data:image/{ext};base64,{data}".format(ext=ext, data=data)
    return src



def decode_image(src):
    import base64
    import re
    import uuid
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        return dict(error="Invalid Image Format.")
    # 2, base64 decoding
    img = base64.urlsafe_b64decode(data)
    # 3, the binary file is saved
    filename = "{}.{}".format(uuid.uuid4(), ext)
    completeName = os.path.join(settings.STATIC_ROOT, filename)
    with open(completeName, "wb") as f:
        f.write(img)
    return filename


def decode_image2(src):
    import re
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", str(src), re.DOTALL)
    ext = result.groupdict().get("ext")
    data = result.groupdict().get("data")
    return data


def ResizeImage(img, size):
    im = decode_image(img)
    from PIL import Image
    from io import StringIO, BytesIO
    file_ext = os.path.splitext(im)
    ext = ['.jpg', '.png', '.jpeg', '.pneg']
    if file_ext[1] not in ext:
        return dict(error="invalid image extension")
    picture_fn = file_ext[0] + file_ext[1]
    picture_path = os.path.join(settings.STATIC_ROOT, im)
    op = Image.open(picture_path)
    width, height = op.size
    if width < size or height < size:
        if os.path.exists(picture_path):
            rv = os.remove(picture_path)
        return dict(error="Invalid image width & height")
    output_size = (size, size)
    re = op.thumbnail(output_size)
    op.save(picture_path)
    stream = encode_image(picture_path)
    if os.path.exists(picture_path):
        rv = os.remove(picture_path)
    return decode_image2(stream)



# delete expired email otp and used ones
def check_email_otp():
    rows = EmailOtp.objects.filter(Q(expd=True) | Q(used=True)) 
    delete_log = [row.delete() for row in rows]
    return delete_log

# delete send otp email in database when request another
def check_email_otp2(email):
    rows = EmailOtp.objects.filter(email=email)
    delete_log = [row.delete() for row in rows]
    return delete_log


class Register(APIView):
    renderer_classes = [JSONRenderer]

    # send email otp for email verification
    @staticmethod
    def get(request):
        delet_otp = check_email_otp()
        name = json.loads(request.body).get('name', None)
        email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
        phone = ValidatePhone(json.loads(request.body).get('phone', None))

        if phone['msg'] == "error":
            msg = dict(msg="Invalid Phone number")
            return Response(msg)
        
        if email == None or email == "" or name == None or name == "" or phone == None or phone == "":
            msg = dict(error='missing email or name or phone')
            return Response(msg)

        try:
            check_if_register = auth_user.objects.get(email=email)
            msg = dict(error='Email already exists')
            return Response(msg)
        except auth_user.DoesNotExist:
            delete_existing_email = check_email_otp2(email)
            gen_otp = get_random_numeric_string(6)
            copy_g = copy.copy(gen_otp)
            context = dict(msg=copy_g, name=name)
            sendcode2 = send_email(email, 'Verify code', 'message', context)
            if sendcode2["msg"] == "success":
                send_otp = EmailOtp.objects.create(code=copy_g, email=email)
                send_otp.save()
                if send_otp:
                    msg = dict(msg="success")
                    return Response(msg)
                else:
                    msg = dict(error='error')
                    return Response(msg)
            else:
                msg = dict(error='error')
                return Response(msg)
        

    # register user class
    @staticmethod
    def post(request):
        delet_otp = check_email_otp()
        name = json.loads(request.body).get('name', None)
        email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
        password = json.loads(request.body).get('password', None)
        phone = ValidatePhone(json.loads(request.body).get('phone', None))
        otp = json.loads(request.body).get('otp', None)
        image = json.loads(request.body).get('image', None)

        if phone['msg'] == "error":
            msg = dict(msg="Invalid Phone number")
            return Response(msg)

        if email == None or email == "" or name == None or name == "" or password == None or password == "" \
            or phone == None or phone == "" or otp == None or otp == "":
            msg = dict(error='missing email or name or password or phone or otp')
            return Response(msg)

        try:
            check_if_register = auth_user.objects.get(email=email)
            msg = dict(error='Email already exists')
            return Response(msg)
        except auth_user.DoesNotExist:
    
            if not EmailOtp.objects.filter(code=otp, email=email, used=False).exists():
                msg = dict(error='Invalid Otp')
                return Response(msg)
            else:
                verify_otp2 = EmailOtp.objects.get(code=otp, email=email, used=False)
                if int(time.time()) > int(verify_otp2.expT):
                    verify_otp2.expd = True
                    verify_otp2.save()
                    msg = dict(error='OTP Expired')
                    return Response(msg)
                else:
                    hash = hash_password(password)
                    copy_hash = copy.copy(hash)

                    regis = auth_user.objects.create(email=email, password=make_password(password),
                        pass_id=copy_hash, phone=phone['msg'], name=name,
                        last_login=now, image=ResizeImage(image, 300) if image != "" else None)
                    regis.save()
                    if regis:
                        add_notify = Notification.objects.create(subject="registration", item_id=regis.id, email=email, 
                            body=f"{name} has completed the signup for Mosabides account", 
                            edit_by=auth_user.objects.get(pk=regis.id), name=name)
                        add_notify.save()
                        verify_otp2.delete()
                        msg = dict(msg="success")
                        return Response(msg)
                    else:
                        msg = dict(error="Unable to register user")
                        return Response(msg)


# delete user bearer token when re-request 
def delete_auth_token(id):
    logs = AuthToken.objects.filter(created_by=id)
    if logs.exists():
        delete_log = [log.delete() for log in logs]
        return dict(msg='success')
    else:
        return dict(msg='success')



# generate refresh token
def generateAccess(id):
    log = auth_user.objects.get(pk=id)
    if log.disabled == True:
        msg = dict(error='Account disabled')
        return Response(msg)
    claims = dict(
    role=log.role ,
    exp= datetime.now() + timedelta(minutes=access_exp),
    email=log.email,
    access=True,
    id=log.pk
        )
    token = jwt.encode(claims, super_secret_key, algorithm="HS256")
    save_access = AuthToken.objects.filter(created_by=log.id, access=True).update(token=token)
    return dict(access=token)




# Login class
class Login(APIView):
    renderer_classes = [JSONRenderer]

    # login function
    @staticmethod
    def get(request):
                
        algo = ['HS256']
        rand = random.choice(algo)

        email = request.query_params.get('email', '').translate({ord(c): None for c in string.whitespace})
        password = request.query_params.get('password', None)

        if email == None or email == "" or password == None or password == "":
            msg = dict(error='Missing email or password')
            return Response(msg)

        try:
            log2 = auth_user.objects.get(email=email)
            decrypt = decrypt_password(log2.pass_id)
            copy_decrypt = copy.copy(decrypt) 
            if not copy_decrypt == password:
                msg = dict(error='Incorrect email or password')
                return Response(msg)
            else:
                if log2.disabled == True:
                    msg = dict(error='Account disabled')
                    return Response(msg)
                else:
                    delete_available_token = delete_auth_token(log2.pk)
                    if delete_available_token['msg'] == "success":
                        claims = dict(
                        role=log2.role,
                        exp= datetime.now() + timedelta(minutes=access_exp),
                        email=log2.email,
                        access=True,
                        id=log2.pk,
                            )
                        token = jwt.encode(claims, super_secret_key, algorithm="HS256")
                        claims2 = dict(
                        role=log2.role,
                        exp= datetime.now() + timedelta(minutes=refresh_exp),
                        email=log2.email,
                        refresh=True,
                        id=log2.pk
                            )
                        token2 = jwt.encode(claims2, super_secret_key, algorithm="HS256")
                        save_access = AuthToken.objects.create(created_by=log2 ,token=token, access=True, refresh=False)
                        save_access.save()
                        save_refresh = AuthToken.objects.create(created_by=log2, token=token2, refresh=True, access=False)
                        save_refresh.save()
                        if save_access and save_refresh:
                            msg = dict(access=token, refresh=token2)
                            return Response(msg)
                    else:
                        msg = dict(error='error')
                        return Response(msg)

        except auth_user.DoesNotExist:
            msg = dict(error='Not registered')
            return Response(msg)
    

    # request refresh token
    @staticmethod
    def post(request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token == None:
            msg = dict(error='Authorization header not supplied')
            return Response(msg)

        token_format = token.split()
        auth_method = token_format[0]
        try:
            token = token_format[1]
        except:
            msg = dict(error='No Auth token found')
            return Response(msg)
        if auth_method == "Bearer":
            try:
                user = jwt.decode(token, super_secret_key, algorithms=['HS256'])
                user_token = AuthToken.objects.filter(token=token, refresh=True, created_by=user["id"])
                if user_token.exists():
                    user_id = user["id"]
                    role_c = ["user", "admin", "superAdmin", "rider"]
                    role = user["role"] if user["role"] in role_c else NotFound()
                    verify = auth_user.objects.get(pk=user_id)
                    newAccessToken = generateAccess(verify.id)
                    return Response(newAccessToken)
                else:
                    msg = dict(error='Refresh Token Required')
                    return Response(msg)
            except jwt.ExpiredSignatureError:
                msg = dict(error='Refresh token Expired')
                return Response(msg)
            except:
                msg = dict(error='Unauthorized Request.')
                return Response(msg)



# check if bearer token is present
def check_http_auth(request):
    token = request.META.get('HTTP_AUTHORIZATION', None)
    if token == None:
        return dict(error='Authorization header not supplied')

    token_format = token.split()
    auth_method = token_format[0]
    try:
        token = token_format[1]
    except:
        return dict(error='No Auth token found')
    if auth_method == "Bearer":
        try:
            user = jwt.decode(token, super_secret_key, algorithms=['HS256'])
            logs = AuthToken.objects.filter(created_by=user["id"], token=token, access=True)
            if logs.exists():
                log = auth_user.objects.get(pk=user["id"])
                if log.disabled == True:
                    return dict(error='Account disabled')
                else:
                    if user["access"] == True:
                        return dict(msg=user)
                    else:
                        return dict(error='Access Token Required')
            else:
                return dict(error='Invalid Token')
        except jwt.ExpiredSignatureError:
            return dict(error='Access Token Expired')
        except:
            return dict(error='Unauthorized Request.')



def check_http_auth2(request):
    token = request.META.get('HTTP_AUTHORIZATION', None)
    if token == None:
        pass
    else:
        token_format = token.split()
        auth_method = token_format[0]
        try:
            token = token_format[1]
        except:
            return dict(error='No Auth token found')
        if auth_method == "Bearer":
            try:
                user = jwt.decode(token, super_secret_key, algorithms=['HS256'])
                logs = AuthToken.objects.filter(created_by=user["id"], token=token, access=True)
                if logs.exists():
                    log = auth_user.objects.get(pk=user["id"])
                    if log.disabled == True:
                        return dict(error='Account disabled')
                    else:
                        if user["access"] == True:
                            return dict(msg=user)
                        else:
                            return dict(error='Access Token Required')
                else:
                    return dict(error='Invalid Token')
            except jwt.ExpiredSignatureError:
                return dict(error='Access Token Expired')
            except:
                return dict(error='Unauthorized Request.')




class Profile(APIView):
    renderer_classes = [JSONRenderer]

    # user get profile details
    @staticmethod
    def get(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)

        try: 
            userD = auth_user.objects.get(pk=claims["msg"]["id"])
            if userD.role not in set:
                msg = dict(error="Unauthorized Request")
                return Response(msg)
            else:

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
                        'duration': od.duration, 'billing_id': od.billing_id.id,
                        'delivery_type': od.delivery_type, 'category': od.category.id,
                        'price': od.price, 'order_id': od.order_id, 'delivery_fee': od.delivery_fee,
                        'total': od.total, 'paid': od.paid, 'image': od.image,
                        'reference': od.reference, 'price_desc': od.price_desc, 'seen': od.seen,
                        'delivery_status': od.delivery_status, 'assigned_to': od.assigned_to.id, 'top_up': od.top_up,
                        'quantity': od.quantity, 'paid': od.paid, 'created_at': od.created_at,
                        'created_by': od.created_by.id,
                    } for od in orders]
                msg = dict(profile=profile, billing=billing, wishlist=wishlist, order=order)
                return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error="Invalid user")
            return Response(msg)


    # user update account
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)

        try: 
            userD = auth_user.objects.get(pk=claims["msg"]["id"])
            if userD.role not in set:
                msg = dict(error="Unauthorized Request")
                return Response(msg)
            else:

                name = json.loads(request.body).get('name', None)
                email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
                phone = ValidatePhone(json.loads(request.body).get('phone', None))
                image = json.loads(request.body).get('image', None)

                if phone['msg'] == "error":
                    msg = dict(msg="Invalid Phone number")
                    return Response(msg)

                if email == None or email == "" or name == None or name == "" or phone == None or phone == "":
                    msg = dict(error='missing email or name or phone')
                    return Response(msg)

                regis = auth_user.objects.filter(pk=userD.pk).update(email=email, phone=phone['msg'], name=name,
                        image=ResizeImage(image, 300) if image != "" else userD.image)
                userD = auth_user.objects.get(pk=userD.pk)
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
                        'duration': od.duration, 'billing_id': od.billing_id.id,
                        'delivery_type': od.delivery_type, 'category': od.category.id,
                        'price': od.price, 'order_id': od.order_id, 'delivery_fee': od.delivery_fee,
                        'total': od.total, 'paid': od.paid, 'image': od.image,
                        'reference': od.reference, 'price_desc': od.price_desc, 'seen': od.seen,
                        'delivery_status': od.delivery_status, 'assigned_to': od.assigned_to.id, 'top_up': od.top_up,
                        'quantity': od.quantity, 'paid': od.paid, 'created_at': od.created_at,
                        'created_by': od.created_by.id,
                    } for od in orders]
                msg = dict(profile=profile, billing=billing, wishlist=wishlist, order=order)
                return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error="Invalid user")
            return Response(msg)


    # user delete account
    @staticmethod
    def delete(request):
        claims = check_http_auth(request)
        set = ["user"]

        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)

        try: 
            userD = auth_user.objects.get(pk=claims["msg"]["id"])
            if userD.role not in set:
                msg = dict(error="Unauthorized Request")
                return Response(msg)
            else:
                delete_user = userD.delete()
                msg = dict(msg='success')
                return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error="Invalid user")
            return Response(msg)


    # user disable account
    @staticmethod
    def post(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)

        try: 
            userD = auth_user.objects.get(pk=claims["msg"]["id"])
            if userD.role not in set:
                msg = dict(error="Unauthorized Request")
                return Response(msg)
            else:
                regis = auth_user.objects.filter(pk=userD.pk).update(disabled=True, disabled_by=userD)
                msg = dict(msg='success')
                return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error="Invalid user")
            return Response(msg)

        


class ChangePassword(APIView):
    renderer_classes = [JSONRenderer]
    # request change password
    @staticmethod
    def post(request):

        delet_otp = check_email_otp()
        email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
        
        if email == None or email == "":
            msg = dict(error='email is required')
            return Response(msg)
        try:
            check_if_register = auth_user.objects.get(email=email)
            delete_existing_email = check_email_otp2(email)
            gen_otp = get_random_numeric_string(6)
            copy_g = copy.copy(gen_otp)
            context = dict(msg=copy_g, name=check_if_register.name)
            sendcode2 = send_email(email, 'Reset password code', 'resetPassword', context)
            if sendcode2["msg"] == "success":
                send_otp = EmailOtp.objects.create(code=copy_g, email=email)
                send_otp.save()
                if send_otp:
                    msg = dict(msg="success")
                    return Response(msg)
                else:
                    msg = dict(error="error")
                    return Response(msg)
            else:
                msg = dict(error='error')
                return Response(msg)

        except auth_user.DoesNotExist:
            msg = dict(error='Email does not exists')
            return Response(msg)
    

    # change password when already logged-in
    @staticmethod
    def put(request):
        claims = check_http_auth(request)
        set = ["user", "admin", "superAdmin", "rider"]

        old = request.query_params.get('old', None)
        new = request.query_params.get('new', None)
        if old == None or old == "" or new == None or new == "":
            msg = dict(error='Missing old_password or new_password')
            return Response(msg)

        if claims == None:
            msg = dict(error='Authorization header not supplied.')
            return Response(msg)
        elif claims.get('error', None) != None:
            return Response(claims)
        
        try: 
            userD = auth_user.objects.get(pk=claims["msg"]["id"])
            if userD.role not in set:
                msg = dict(error="Unauthorized Request")
                return Response(msg)
            else:
                decrypt = decrypt_password(userD.pass_id)
                copy_decrypt = copy.copy(decrypt) 
                if not copy_decrypt == old:
                    msg = dict(msg="Invalid password")
                    return Response(msg)
                else:
                    hash = hash_password(new)
                    copy_hash = copy.copy(hash)
                    regis = auth_user.objects.filter(pk=userD.pk).update(pass_id=copy_hash)
                    msg = dict(msg='success')
                    return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error="Invalid user")
            return Response(msg)




class VerifyPassword(APIView):
    renderer_classes = [JSONRenderer]
    # verify otp reset password
    @staticmethod
    def get(request):
        delet_otp = check_email_otp()

        email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
        otp = json.loads(request.body).get('otp', None)

        if email == None or email == "" or otp == None or otp == "":
            msg = dict(error='missing email or otp')
            return Response(msg)

        try:
            check_if_register = auth_user.objects.get(email=email)
            if not EmailOtp.objects.filter(code=otp, email=email, used=False).exists():
                msg = dict(error='Invalid Otp')
                return Response(msg)
            else:
                verify_otp2 = EmailOtp.objects.get(code=otp, email=email, used=False)
                if int(time.time()) > int(verify_otp2.expT):
                    verify_otp2.expd = True
                    verify_otp2.save()
                    msg = dict(error='OTP Expired')
                    return Response(msg)
                else:
                    update_otp = EmailOtp.objects.filter(code=otp, email=email, used=False).update(used=True)
                    msg = dict(msg="success")
                    return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error='Email does not exists')
            return Response(msg)
            

    @staticmethod
    def post(request):
    
        email = json.loads(request.body).get('email', '').translate({ord(c): None for c in string.whitespace})
        otp = json.loads(request.body).get('otp', None)
        password = json.loads(request.body).get('password', None)

        if email == None or email == "" or otp == None or otp == "" or password == None or password == "":
            msg = dict(error='missing email or otp or password')
            return Response(msg)
        try:
            check_if_register = auth_user.objects.get(email=email)
            if not EmailOtp.objects.filter(code=otp, email=email, used=True).exists():
                msg = dict(error='Invalid Otp')
                return Response(msg)
            else:
                verify_otp2 = EmailOtp.objects.get(code=otp, email=email, used=True)
                hash = hash_password(password)
                copy_hash = copy.copy(hash)
                save_email = AddPendingEmail.objects.create(status="pending", email=check_if_register.email, subject="reset_password")
                add_notify = Notification.objects.create(subject="Reset-password", item_id=check_if_register.pk,
                    email=check_if_register.email, body=f"{check_if_register.name} Reset his/her password",
                    edit_by=check_if_register, name=check_if_register.name)
                regis = auth_user.objects.filter(pk=check_if_register.pk).update(pass_id=copy_hash)
                save_email.save()
                add_notify.save()
                verify_otp2.delete()
                msg = dict(msg="success")
                return Response(msg)
        except auth_user.DoesNotExist:
            msg = dict(error='Email does not exists')
            return Response(msg)





class HelloView(APIView):
    # permission_classes = (IsAuthenticated,)
    renderer_classes = [JSONRenderer]

        # if check_if_register:
        #     content = {
        #         'id': check_if_register.id, 'email': check_if_register.email, 'name': check_if_register.name,
        #         'role': check_if_register.role, 'phone': check_if_register.phone, 'subscribe_news': check_if_register.subscribe_news,
        #         'purchase': check_if_register.purchase, 'seen': check_if_register.seen, 'image': check_if_register.image,
        #         'last_login': check_if_register.last_login, 'is_staff': check_if_register.is_staff, 'updated_by': check_if_register.updated_by,
        #         'disabled': check_if_register.disabled, 'disabled_by': check_if_register.disabled_by, 'created_at': check_if_register.created_at
        #     }
        #     context = dict(msg=content)
        # else:
        #     context = dict(error='error')
    @staticmethod
    def get(request):
        # 'name': request.GET.get('name', None),   # worked for  http://127.0.0.1:8000/api/user/sendOtp/?name=dsdd&email=ddsfds
        # 'name': request.query_params.get('name', None),   # worked for  http://127.0.0.1:8000/api/user/sendOtp/?name=dsdd&email=ddsfds
        # all_data = json.loads(request.body)
        # data = json.loads(request.body)[0]
        # wishlists =Wishlist.objects.filter(product_id__in=Product.objects.all(), created_by=2)

        # user = get_user_model().objects.create(email="olorunsholamatins@gmail.com", password="matins12173",
        #     name="matins", pass_id="matins12173", phone="123456789", image="dfdsfdsf")
        # save = user.save()
        context = {
            'msg': 'sddsd',
            'name': 'dsfdsfd'
        }
        # email = send_email('olorunsholamatins@gmail.com', 'testing', 'demo', context)
        # image = json.loads(request.body).get('image', None)
        # image2 = ResizeImage(image, 768)
        # user = hash_password('password')
        # user = decrypt_password(password)
        content = {'password': context}
        return JsonResponse(content)