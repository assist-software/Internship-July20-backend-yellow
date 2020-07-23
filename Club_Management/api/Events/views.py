from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from Events.models import Events, Participants, Workout
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from users.models import User
from Club.models import Club
from Athletes.models import Sports
from Club.models import MembersClub
from django.views.decorators.csrf import csrf_exempt
from Events.serializers import EventsSerializer
from api.permissions import AdminORCoachPermission, AthletePermission, CoachPermission


@csrf_exempt
@api_view(['POST'])
@permission_classes([AdminORCoachPermission, ])
def event_post(request):
    """ Create new event.
    Just Admins and Coaches have access. """

    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)
    if request.method == "POST":

        event = Events(club_id=Club.objects.get(name=request.data.get('club')), name=request.data.get('name'),
                       description=request.data.get('description'),
                       location=request.data.get('location'), date=request.data.get('date'),
                       time=request.data.get('time'),
                       sport_id=Sports.objects.get(description=request.data.get('sport')))
        event.save()
        serializers = EventsSerializer(data=event.__dict__)
        if serializers.is_valid():
            print("Serializers data  {}".format(serializers.data))
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AthletePermission, ])
def event_join(request, id_event):
    """ Joining an event by ID:
        Just the ATHLETE has access to access the join path and he will be registered
        in a list of participants the requested to register at the events."""

    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)

    ev = Events.objects.get(id=id_event)
    try:
        mem_cl = MembersClub.objects.get(id_club=ev.club_id, id_User=user)
        if Participants.objects.filter(event=ev, member=mem_cl):
            return Response({"Your requested already to join this event."})
        else:
            new_request = Participants(event=ev, member=mem_cl, is_invited=False,
                                       is_requested=True, is_participant=False)
            new_request.save()
            return Response({"Your request had been registered"}, status=status.HTTP_202_ACCEPTED)
    except MembersClub.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AthletePermission, ])
def event_get(request):
    """Listing all events for all joined clubs.
    The endpoint should be accessible by all authenticated Athletes.
    """
    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)

    clubs = list(MembersClub.objects.filter(id_User=user).values("id_club"))
    final_list = list()
    for club in clubs:
        ev = list(Events.objects.filter(club_id=club["id_club"]).values("name", "description", "location",
                                                                        "date", "time", "sport_id"))
        for i in ev:
            i["sport_id"] = Sports.objects.get(id=i["sport_id"]).description
        final_list.append(ev)

    if request.method == 'GET':
        return JsonResponse(final_list, safe=False)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes((CoachPermission, ))
def event_delete(request, id_event):
    """ Delete an event.
    The endpoint should be accessible by all authenticated Coaches
    """

    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)
    if request.method == "DELETE":
        try:
            event = Events.objects.get(id=id_event)
            event.delete()
            return Response({'success': 'The event was removed.'}, status=HTTP_200_OK)
        except Events.DoesNotExist:
            return Response({'error': 'Event does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:
        pass


@csrf_exempt
@api_view(['GET'])
@permission_classes((CoachPermission,))
def event_get_detail(request, id_event):
    """ Get event info and a list of athletes that have
    requested to join the event.
    The endpoint should be accessible by all authenticated Coaches."""

    if request.method == "GET":
        try:
            events = list(Events.objects.filter(id=id_event).values("id", "name", "description", "location",
                                                                    "date", "time", "sport_id"))
            final_list = list()
            final_list.append(events)

            for e in events:
                participants = list(Participants.objects.filter(event=e["id"], is_requested=True).values("member"))
                for p in participants:
                    part_list = list(MembersClub.objects.filter(id=p["member"]).values("id_User"))
                    for d in part_list:
                        detail_list = list(User.objects.filter(id=d["id_User"]).values("first_name", "last_name",
                                                                                       "email", "height", "weight",
                                                                                       "age", "role", "gender",
                                                                                       "primary_sport",
                                                                                       "secondary_sport"))
                        for part in detail_list:
                            if part["gender"] == User.MALE:
                                part["gender"] = "Male"
                            else:
                                part["gender"] = "Female"

                        final_list.append(detail_list)

            return JsonResponse(final_list, safe=False)
        except Events.DoesNotExist:
            return Response({'error': 'Event does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:
        pass


@csrf_exempt
@api_view(['PUT'])
@permission_classes((CoachPermission,))
def event_put(request, id_event):
    """Edit an event by id.
    The endpoint should be accessible by all authenticated Coaches
    """
    if request.method == "PUT":
        event = (get_object_or_404(Events, id=id_event))
        event.club_id = Club.objects.get(name=request.data.get('club'))
        event.name = request.data.get('name')
        event.description = request.data.get('description')
        event.location = request.data.get('location')
        event.date = request.data.get('date')
        event.time = request.data.get('time')
        event.sport_id = Sports.objects.get(description=request.data.get('sport'))

        event.save()
        return Response(status=HTTP_200_OK)


# workout
@csrf_exempt
@api_view(['POST'])
@permission_classes([AthletePermission, ])
def workout_post(request):
    """ Register an athlete progress for the event.
    The endpoint should be accessible by all authenticated Athletes """

    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)

    if request.method == "POST":
        workout = Workout(owner=user, name=request.data.get('name'), description=request.data.get('description'),
                          event=Events.objects.get(name=request.data.get('event')),
                          latitude=request.data.get('latitude'),
                          longitude=request.data.get('longitude'), radius=request.data.get('radius'),
                          duration=request.data.get('duration'), distance=request.data.get('distance'),
                          average_hr=request.data.get('average_hr'),
                          calories_burned=request.data.get('calories_burned'),
                          average_speed=request.data.get('average_speed'),
                          workout_effectiveness=request.data.get('workout_effectiveness'),
                          heart_rate=request.data.get('heart_rate'))
        workout.save()
        serializers = EventsSerializer(data=workout.__dict__)
        if serializers.is_valid():
            print("Serializers data  {}".format(serializers.data))
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AthletePermission,))
def get_detail_workout(request):
    """ List workout history for an Athlete.
    The endpoint should be accessible by all authenticated Athletes """

    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)
    workout = list(Workout.objects.filter(owner=user).values("name", "event", "latitude", "longitude", "radius",
                                                             "duration", "distance", "average_hr", "calories_burned",
                                                             "average_speed", "workout_effectiveness", "heart_rate"))
    for w in workout:
        w["event"] = Events.objects.get(id=w["event"]).date

    if request.method == 'GET':
        return JsonResponse(workout, safe=False)
