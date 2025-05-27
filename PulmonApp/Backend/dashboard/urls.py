from django.urls import path
from .views import TestView, UserView, auth_status
from rest_framework.authtoken.views import obtain_auth_token  # Import DRF token auth view

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('auth/user/', UserView.as_view(), name='user'),
    path('auth/status/', auth_status, name='auth_status'),
    path('auth/login/', obtain_auth_token, name='api_token_auth'),  # Replace LoginView
   ]
