from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from Club.models import Club,Members_club
import users
from users import models
from django.contrib.auth.models import User

def get_image_path(instance,filename):
    return os.path.join('photos',str(instance.id),filename)

GENDER=[
        ("M",'male'),
        ("F",'female'),
    ]

class AthleteSerializer(serializers.Serializer):
    gender=serializers.ChoiceField(choices=GENDER)
    id=serializers.IntegerField(read_only=True)
    name=serializers.CharField(max_length=200,required=True)
    email_adress=serializers.CharField(max_length=45,required=True)
    primary_sport=serializers.CharField(max_length=45,required=True)
    secondary_sport=serializers.CharField(max_length=45,required=True)
    age = serializers.IntegerField()
    height = serializers.IntegerField()
    weight = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(400)])
    #profile_image=serializers.ImageField(upload_to=get_image_path)

    def Create(self,validated_data):
        return users.objects.create(**validated_data)