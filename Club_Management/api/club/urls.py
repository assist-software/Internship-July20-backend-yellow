from django.urls import path
from .views import create_club, show_club, join_club, mb_requested_club, clubs

urlpatterns = [
    path('club/', create_club, name='create'),
    path("club/<int:club_id>/", show_club, name="show club"),
    path("club/<int:club_id>/join/", join_club, name="join club"),
    path("club/<int:club_id>/requested/", mb_requested_club, name="Show athletes that request to join club"),
    path("club/clubs/", clubs, name="Return list of clubs"),
    path("club/accept/", clubs, name="Accept request")

]