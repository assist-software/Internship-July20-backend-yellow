from rest_framework import serializers
from Club.models import Club, MembersClub


class ClubSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30, required=True)

    def create(self, validated_data):
        return Club.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        return instance


""" Validation for the lists of invited/requested/members of the club. An ATHLETE can't be all at the same time. """


def validate_status(attrs):
    if attrs['is_invited'] + attrs['is_requested'] + attrs['is_member'] != 1:
        raise serializers.ValidationError("Just one option may be selected")
    return attrs


class MembersClubSerializer(serializers.Serializer):
    is_invited = serializers.BooleanField(default=False)
    is_requested = serializers.BooleanField(default=False)
    is_member = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return MembersClub(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        return instance
