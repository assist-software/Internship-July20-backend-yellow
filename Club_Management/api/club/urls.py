from django.urls import path
from .views import create_club, show_club, join_club

urlpatterns = [
    path('club/', create_club, name='create'),
    path("club/<int:club_id>", show_club, name="show club"),
    path("club/<int:club_id>/join/", join_club, name="join club")
]