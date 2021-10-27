from django.urls import path
from adminUser import views

app_name = 'adminUser'

urlpatterns = [
    path('ALL_ITEM/', views2.ALL_ITEM.as_view(), name='all-item'),
]