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
# from passlib.hash import pbkdf2_sha256
import random
from django.db.models import Q
from core.models import Product, ContactUs, EmailOtp, Notification, Test


now = datetime.now()
# jwt secret key
super_secret_key = os.getenv('JWT')
# user model function
auth_user = get_user_model()
# server email sender email
EMAIL_SENDER = os.getenv('EMAIL_HOST_USER')
# salt for password hashing
salt = bytes(os.getenv('SALT'), 'utf-8')

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
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,
        dklen=20
    )
    return key


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
    completeName = os.path.join(request.folder,'demo/static', filename)
    with open(completeName, "wb") as f:
        f.write(img)
    return filename



def ResizeImage(img, size):
    im = decode_image(img)
    from PIL import Image
    from io import StringIO, BytesIO
    file_ext = os.path.splitext(im)
    ext = ['.jpg', '.png', '.jpeg', '.pneg']
    if file_ext[1] not in ext:
        return dict(error="invalid image extension")
    picture_fn = file_ext[0] + file_ext[1]
    picture_path = os.path.join(settings.STATIC_URL, im)
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
    return decode_image(stream)



# delete expired email otp and used ones
def check_email_otp():
    rows = EmailOtp.objects.filter(Q(expd=True) | Q(used=True) ) 
    for row in rows:
        row.delete()

# delete send otp email in database when request another
def check_email_otp2(email):
    rows = EmailOtp.objects.filter(email=email)
    for row in rows:
        row.delete()



class Register(APIView):
    renderer_classes = [JSONRenderer]

    # TODO add password correctly and validate phone
    # send email otp for email verification
    @staticmethod
    def get(request):
        delet_otp = check_email_otp()
        msg = dict()
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
            msg = dict(error='email already exists')
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
                    msg = dict(error="error")
                    return Response(msg)
            else:
                msg = dict(error="error")
                return Response(msg)
        


    # TODO add password correctly and validate phone
    # register user class
    @staticmethod
    def post(request):
        delet_otp = check_email_otp()
        msg = dict()
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
            msg = dict(error='email already exists')
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
                            edit_by=auth_user.objects.get(pk=regis.id),name=name)
                        add_notify.save()
                        verify_otp2.delete()
                        msg = dict(msg="success")
                        return Response(msg)
                    else:
                        msg = dict(error="Unable to register user")
                        return Response(msg)




# TODO install module passlib,
# Login class
class Login(APIView):
    renderer_classes = [JSONRenderer]
    @staticmethod
    def get(request):
                
        algo = ['HS256']
        rand = random.choice(algo)

        email = request.query_params.get('email', '').translate({ord(c): None for c in string.whitespace})
        password = request.query_params.get('password', None)

        if email == None or email == "" or password == None or password == "":
            msg = dict(error='Missing email or password')
            return Response(msg)

        hash = hash_password(password)
        copy_hash = copy.copy(hash)

        try:
            log2 = auth_user.objects.get(email=email)
            log = auth_user.objects.filter(email=email, pass_id=copy_hash)
            if not log.exists():
                msg = dict(error='Incorrect email or password')
                return Response(msg)
            else:
                if log2.disabled == True:
                    msg = dict(error='Account disabled')
                    return Response(msg)
                else:
                    claims = dict(
                    role=log2.role,
                    exp= datetime.now() + timedelta(minutes=5),
                    email=log2.email,
                    access=True,
                    id=log2.pk,
                        )
                    token = jwt.encode(claims, super_secret_key, algorithm="HS256")
                    claims2 = dict(
                    role=log2.role,
                    exp= datetime.now() + timedelta(minutes=60*24),
                    email=log2.email,
                    refresh=True,
                    id=log2.pk
                        )
                    token2 = jwt.encode(claims2, super_secret_key, algorithm="HS256")
                    msg = dict(access=token, refresh=token2)
                    return Response(msg)

        except auth_user.DoesNotExist:
            msg = dict(error='Not registered')
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

        # user = get_user_model().objects.create(email="olorunsholamatins@gmail.com", password="matins12173",
        #     name="matins", pass_id="matins12173", phone="123456789", image="dfdsfdsf")
        # save = user.save()
        # context = {
        #     'password': password
        # }
        # email = send_email('olorunsholamatins@gmail.com', 'testing', 'demo', context)
        # user = "success"
        content = {'message': "success"}
        return JsonResponse(content)