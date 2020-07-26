from django.urls import include, path
from api.Swagger.views import schema_view_docs
from django.urls import path, include, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Club Management API",
        default_version='v1',
        description="Welcome to the world of Club Management",
        terms_of_service="https://www.ClubManagement.org",
        contact=openapi.Contact(email="ClubM@ClubM.org"),
        license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger-ui/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger'),
    path('docs/', schema_view_docs),
    path('', include('api.users.urls')),
    path('', include('api.club.urls')),
    path('', include('api.Coach.urls')),
    path('', include('api.Athletes.urls')),
    path('', include('api.Events.urls')),
]
