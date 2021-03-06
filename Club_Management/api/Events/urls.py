from django.urls import path
from .views import event_get, event_post, event_join, event_get_detail, event_put, event_delete, event_get_all_events, \
    has_events, event_get_is_member
from .views import workout_post, get_detail_workout


urlpatterns = [
    path('event/create/', event_post, name='create'),
    path('event/view/', event_get, name='all events for an user'),
    path('event/delete/<int:id_event>/', event_delete, name='delete event'),
    path('event/detail/<int:id_event>/', event_get_detail, name='detail event'),
    path('event/join/<int:id_event>/', event_join, name='join event'),
    path('event/put/<int:id_event>/', event_put, name='edit event'),
    path('workout/create/', workout_post, name='create workout'),
    path('workout/view/', get_detail_workout, name='detail workout'),
    path('event/all/events/', event_get_all_events, name='all events'),
    path('event/has_events/', has_events, name='all events'),
    path('event/is_member/', event_get_is_member, name='all events where an athlete is member'),

]
