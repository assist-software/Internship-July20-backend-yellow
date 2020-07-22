from rest_framework import serializers
from Events.models import *
from Athletes.models import Sports
from Club.serializers import ClubSerializer


class EventsSerializer(serializers.Serializer):
    id_event = serializers.IntegerField(read_only=True)
    #club_id= ClubSerializer()
    name = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=300)
    location = serializers.CharField(max_length=300,required=False)
    date = serializers.DateField(required=False)
    time = serializers.TimeField(required=False)
    #sport_id = SportsSerializer()

    def create(self, validated_data):
        return Events.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.date = validated_data.get('date', instance.date)
        instance.time = validated_data.get('time', instance.time)
        instance.save()
        return instance


class ParticipantsSerializer(serializers.Serializer):
    is_invited = serializers.BooleanField(default=False)
    is_requested = serializers.BooleanField(default=False)
    is_member = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return ParticipantsSerializer.ojects.create(**validated_data)

    def validate_status(self, attrs):
        if attrs['is_invited']+attrs['is_requested']+attrs['is_member'] != 1:
            raise serializers.ValidationError("Just one option must be selected")
        return attrs


class WorkoutSerializer(serializers.Serializer):
    id_workout = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=300)
    # event = serializers.ForeignKey(Events, on_delete=models.CASCADE)
    latitude = serializers.IntegerField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = serializers.IntegerField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    radius = serializers.IntegerField(default=0)
    duration = serializers.IntegerField(default=0)
    distance = serializers.IntegerField(default=0)
    average_hr = serializers.IntegerField(default=0)
    calories_burned = serializers.IntegerField(default=0)
    average_speed = serializers.IntegerField(default=0)
    workout_effectiveness = serializers.IntegerField(default=0)
    heart_rate = serializers.IntegerField()

    def create(self, validated_data):
        return WorkoutSerializer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.description)
        instance.description = validated_data.get('description', instance.description)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.radius = validated_data.get('radius', instance.radius)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.distance = validated_data.get('distance', instance.distance)
        instance.average_hr = validated_data.get('average_hr', instance.average_hr)
        instance.calories_burned = validated_data.get('calories_burned', instance.calories_burned)
        instance.average_speed = validated_data.get('average_speed', instance.average_speed)
        instance.workout_effectiveness = validated_data.get('workout_effectiveness', instance.workout_effectiveness)
        instance.heart_rate = validated_data.get('heart_rate', instance.heart_rate)

        return instance
