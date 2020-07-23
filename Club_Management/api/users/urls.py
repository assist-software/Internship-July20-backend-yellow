from django.urls import path
from .views import signin, reset_password, invite

urlpatterns = [
    path('signin/', signin, name='login'),
    path('reset-password/', reset_password, name='reset-password'),
    path('invite/', invite, name='invite'),
]