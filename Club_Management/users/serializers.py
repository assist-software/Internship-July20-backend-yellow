from rest_framework import serializers
from . import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField()
    height = serializers.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(400)], required=False)
    weight = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(400)], required=False)
    age = serializers.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)], required=False)
    primary_sport = serializers.IntegerField(read_only=True, default=None)
    secondary_sport = serializers.IntegerField(read_only=True, default=None)
    role = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        user = models.User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            height=validated_data['height'],
            weight=validated_data['weight'],
            age=validated_data['age'],
            password=validated_data['password'],
            is_active=False)
        return user
