from django.urls import path
from .views import coach, delete_edit

urlpatterns = [
    path('coach/', coach, name='Create new coach, or return all coaches.'),
    path('coach/<int:id>/', delete_edit, name='Delete coach or edit.'),
]