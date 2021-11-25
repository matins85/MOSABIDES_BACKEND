from django.urls import path
from user import views, views2

app_name = 'user'

urlpatterns = [
    path('create/', views.HelloView.as_view(), name='create'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('refresh/', views.Login.as_view(), name='refresh'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('changePassword/', views.ChangePassword.as_view(), name='change-password'),
    path('verifyPassword/', views.VerifyPassword.as_view(), name='verify-password'),
    path('emailUs/', views2.Contact_Us.as_view(), name='email-us'),
    path('wishlist/', views2.AddWishlist.as_view(), name='wishlist'),
    path('billing/', views2.Billing.as_view(), name='billing'),
    path('updateDelete/', views2.Update_delete.as_view(), name='update-delete'),
    path('addReview/', views2.AddRewview.as_view(), name='add-review'),
    path('order/', views2.OrderPurchase.as_view(), name='order'),
]

