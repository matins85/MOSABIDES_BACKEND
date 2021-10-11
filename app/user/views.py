# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model
from core.models import Product, ContactUs
from django.http import JsonResponse


class HelloView(APIView):
    # permission_classes = (IsAuthenticated,)
    renderer_classes = [JSONRenderer]

    def get(self, request):
        # user = get_user_model().objects.create(email="olorunsholamatins@gmail.com", password="matins12173",
        #     name="matins", pass_id="matins12173", phone="123456789", image="dfdsfdsf")
        # save = user.save()
        user = "dsjndsfdsf"
        content = {'message': user}
        return JsonResponse(content)