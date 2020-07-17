from django.urls import path
from .views import *

urlpatterns = [
    path('signin/', signin, name='login'),
    path('reset-password/', reset_password, name='reset-password'),
    path('invite/', invite, name='invite'),
]