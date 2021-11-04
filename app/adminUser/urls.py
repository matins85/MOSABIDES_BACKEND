from django.urls import path
from adminUser import views

app_name = 'adminUser'

urlpatterns = [
    path('ALL_ITEM/', views.ALL_ITEM.as_view(), name='all-item'),
    path('AddStaff/', views.AddStaff.as_view(), name='add-staff'),
    path('AddRider/', views.AddRider.as_view(), name='add-rider'),
]