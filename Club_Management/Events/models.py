from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
from Club.models import Club, MembersClub
from Athletes.models import Sports


class Events(models.Model):
    club_id = models.ForeignKey('Club.Club', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    date = models.DateField()
    time = models.TimeField()
    sport_id = models.ForeignKey(Sports, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Participants(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    member = models.ForeignKey(MembersClub, on_delete=models.CASCADE)  # after push, Members_club = MembersClub
    is_invited = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=False)


class Workout(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=300)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    latitude = models.IntegerField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.IntegerField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    radius = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    distance = models.IntegerField(default=0)
    average_hr = models.IntegerField(default=0)
    calories_burned = models.IntegerField(default=0)
    average_speed = models.IntegerField(default=0)
    workout_effectiveness = models.IntegerField(default=0)
    heart_rate = models.IntegerField()