from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.HelloView.as_view(), name='create'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
]

