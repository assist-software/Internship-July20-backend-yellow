from django.urls import path
from api.Athletes.views import athlete, delete_edit, register

urlpatterns = [
    path('athlete/', athlete, name="Create a new athlete"),
    path('athlete/<int:id>/', delete_edit, name="Delete Athlete"),
    path('athlete/register/', register, name='Register Athlete')
]