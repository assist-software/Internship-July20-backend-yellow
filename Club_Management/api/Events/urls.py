from django.urls import path, include
from django.conf.urls import url
from .views import *


urlpatterns = [
    path('event/create/', event_post, name='create'),
    path('event/view/', event_get, name='all events for an user'),
    path('event/delete/<int:id_event>/', event_delete, name='delete event'),
    path('event/detail/<int:id_event>/', event_get_detail, name='detail event'),
    path('event/join/<int:id_event>/', event_join, name='join event'),
    path('event/put/<int:id_event>/', event_put, name='edit event'),
    path('workout/create/', workout_post, name='create workout'),

]
