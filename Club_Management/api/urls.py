from django.urls import include, path

urlpatterns = [
    path('', include('api.users.urls')),
    path('', include('api.club.urls')),
    path('', include('api.Coach.urls')),
    path('', include('api.Athlets.urls')),
    path('', include('api.Events.urls')),
]