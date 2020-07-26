from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.validators import MinValueValidator, MaxValueValidator
from Athletes.models import Sports
from users import models


MALE = 0
FEMALE = 1

GENDERS = [
        (MALE, 'Male'),
        (FEMALE, 'Female')
    ]


class SportSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Sports.objects.create(**validated_data)


class AthleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    last_name = serializers.CharField(max_length=200, required=True)
    first_name = serializers.CharField(max_length=200, required=True)
    age = serializers.IntegerField()
    height = serializers.IntegerField()
    weight = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(400)])
    gender = serializers.CharField(max_length=10, required=True)
    email = serializers.CharField(max_length=255, required=True)
    primary_sport = serializers.CharField(max_length=10, required=True)
    secondary_sport = serializers.CharField(max_length=10, required=True)
    #profile_image=serializers.ImageField(upload_to=get_image_path)

    def create(self, validated_data):
        return models.User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('gender', instance.description)
        instance.first_name = validated_data.get('first_name', instance.name)
        instance.last_name = validated_data.get('last_name', instance.name)
        instance.last_name = validated_data.get('last_name', instance.name)
        instance.email = validated_data.get('email', instance.name)
        instance.primary_sport = validated_data.get('primary_sport', instance.name)
        instance.secondary_sport = validated_data.get('secondary_sport', instance.name)
        instance.age = validated_data.get('age', instance.name)
        instance.height = validated_data.get('height', instance.name)
        instance.weight = validated_data.get('weight', instance.name)
        return instance

