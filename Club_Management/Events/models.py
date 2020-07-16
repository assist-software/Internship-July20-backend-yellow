from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from Club_Management.user_auth.models import *
from Club_Management.Athlets.models import *
from Club_Management.Club.models import *

# Create your models here.


class Events(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    location = models.CharField(max_length = 300)
    date = models.DateTimeField('date events')
    time = models.DateTimeField('time events')
    sport = models.ForeignKey(Sports, on_delete=models.CASCADE)
    participants = models.ForeignKey('Events.Participants', on_delete=models.CASCADE)


class Participants(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    member = models.ForeignKey(Members_club, on_delete=models.CASCADE)
    is_invited = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)


class Workout(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    latitude = models.IntegerField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.IntegerField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    radius = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    distance = models.IntegerField(default=0)
    avarage_hr = models.IntegerField(default=0)
    calories_burned = models.IntegerField(default=0)
    avarage_speed = models.IntegerField(default=0)
    workout_effectivnes = models.IntegerField(default=0)
    heart_rate = models.IntegerField()

