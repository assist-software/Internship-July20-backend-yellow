from django.db import models
from rest_framework import serializers


class Club (models.Model):
    name = models.CharField(max_length=30)
    description =  models.CharField(max_length=300)
    id_User = models.ForeignKey('user_auth.User', on_delete=models.CASCADE)


class Members_club(models.Model):
    id_User = models.ForeignKey('user_auth.User', on_delete=models.CASCADE)
    id_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    is_invited = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
