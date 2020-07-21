from django.urls import path, include
from django.conf.urls import url
from .views import *

urlpatterns = [
    path('club/', create_club, name='create'),
    path("club/<int:club_id>", show_club, name="show club"),
    path("club/<int:club_id>/join/", join_club, name="join club")
]