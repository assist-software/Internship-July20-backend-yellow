from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.validators import MinValueValidator, MaxValueValidator
import os
import users
from users.models import User
from django.contrib.auth.models import User


class SportSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return users.objects.create(**validated_data)


class AthleteSerializer(serializers.Serializer):
    gender = serializers.IntegerField()
    id = serializers.IntegerField(read_only=True)
    last_name = serializers.CharField(max_length=200, required=True)
    first_name = serializers.CharField(max_length=200, required=True)
    email = serializers.CharField(max_length=255, required=True)
    primary_sport = SportSerializer()
    secondary_sport = SportSerializer()
    age = serializers.IntegerField()
    height = serializers.IntegerField()
    weight = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(400)])
    #profile_image=serializers.ImageField(upload_to=get_image_path)

    def create(self, validated_data):
        return users.objects.create(**validated_data)


