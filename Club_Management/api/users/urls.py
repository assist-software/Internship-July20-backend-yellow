from django.urls import path, include
from django.conf.urls import url
from .views import *

urlpatterns = [
    path('signin/', CustomLoginView.as_view(), name='login'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    #path('reset-password/confirm/', CustomPasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    #url('', include('django.contrib.auth.urls')),
]