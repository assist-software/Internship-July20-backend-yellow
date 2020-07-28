from django.db import models
from rest_framework import serializers

from users.models import User


class Club(models.Model):
    name = models.CharField(max_length=30, unique=True)
    id_Owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


"""Model for the lists of invited/requested/members of the club."""


class MembersClub(models.Model):
    id_User = models.ForeignKey(User, on_delete=models.CASCADE)
    id_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    is_invited = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
