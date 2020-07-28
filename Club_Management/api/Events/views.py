from datetime import datetime, timedelta, date
from math import ceil

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from Events.models import Events, Participants, Workout
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from users.models import User
from Club.models import Club
from Athletes.models import Sports
from Club.models import MembersClub
from django.views.decorators.csrf import csrf_exempt
from Events.serializers import EventsSerializer
from rest_framework.permissions import IsAuthenticated
from api.permissions import AdminORCoachPermission, AthletePermission, CoachPermission, AdminPermission, AllPermission
from Events.models import Workout


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminORCoachPermission, ])
def event_post(request):
    """ Create new event.
    Just Admins and Coaches have access. """

    if request.method == "POST":
        name = request.data.get('name')
        description = request.data.get('description')
        location = request.data.get('location')
        date = request.data.get('date')
        time = request.data.get('time')
        if name is None or description is None or location is None or date is None or time is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            club = Club.objects.get(name=request.data.get('club'))
        except Club.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        try:
            event = Events.objects.get(name=name)
            return Response({"error": "Name already exists!"},status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist:
            event = Events(club_id=club, name=name,
                           description=description,
                           location=location, date=date,
                           time=time,)
            event.save()
            return Response(status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, AthletePermission, ])
def event_join(request, id_event):
    """ Joining an event by ID:
        Just the ATHLETE has access to access the join path and he will be registered
        in a list of participants the joined at the events."""
    ev = Events.objects.get(id=id_event)
    try:
        mem_cl = MembersClub.objects.get(id_club=ev.club_id, id_User=request.user)
        if Participants.objects.filter(event=ev, member=mem_cl, is_participant=True):
            old_request = Participants.objects.filter(event=ev, member=mem_cl, is_participant=True)
            old_request.delete()
            new_request = Participants(event=ev, member=mem_cl, is_invited=False,
                                       is_requested=False, is_participant=False)
            new_request.save()
            return Response({"User unjoined."})
        else:
            old_request = Participants.objects.filter(event=ev, member=mem_cl, is_participant=False)
            old_request.delete()
            new_request = Participants(event=ev, member=mem_cl, is_invited=False,
                                       is_requested=False, is_participant=True)
            new_request.save()
            return Response({"User joined"}, status=status.HTTP_202_ACCEPTED)
    except MembersClub.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AthletePermission, IsAuthenticated])
def event_get(request):
    """Listing all events for all joined clubs.
    The endpoint should be accessible by all authenticated Athletes.
    """
    clubs = list(MembersClub.objects.filter(id_User=request.user, is_member=True).values("id_club", "id"))
    final_list = list()
    for club in clubs:
        ev = list(Events.objects.filter(club_id=club["id_club"]).values("id", "club_id", "name", "location",
                                                                        "date"))
        for event in ev:
            part = Participants.objects.filter(event=event["id"], member=club["id"], is_participant=True)
            if not part:
                final_list.append(event)
            else:
                pass
    return JsonResponse(final_list, safe=False)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AthletePermission, ])
def event_get_is_member(request):
    """List all events in which the user is participating.
    The endpoint should be accessible by all authenticated Athletes.
    """
    clubs = list(MembersClub.objects.filter(id_User=request.user).values("id_club", "id"))
    final_list = list()
    for club in clubs:
        ev = list(Events.objects.filter(club_id=club["id_club"]).values("id", "club_id", "name", "location",
                                                                        "date"))
        for event in ev:
            part = Participants.objects.filter(event=event["id"], member=club["id"], is_participant=True)
            if part:
                final_list.append(event)
            else:
                pass
    if request.method == 'GET':
        return JsonResponse(final_list, safe=False)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes((IsAuthenticated, CoachPermission,))
def event_delete(request, id_event):
    """ Delete an event.
    The endpoint should be accessible by all authenticated Coaches
    """

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
@permission_classes((IsAuthenticated, AllPermission))
def event_get_detail(request, id_event):
    """ Get event info and a list of athletes that have
    requested to join the event.
    The endpoint should be accessible by all authenticated Coaches."""
    if request.method == "GET":
        try:
            events = list(Events.objects.filter(id=id_event).values("id", "name", "description", "location",
                                                                    "date", "time", "sport_id"))
            event = events[0]
            f_list = {
                "id": id_event,
                "name": event["name"],
                "description": event["description"],
                "location": event["location"],
                "date": event["date"],
                "time": event["time"]}
            participant_list = list()
            participants = list(Participants.objects.filter(event=event["id"], is_participant=True).values("member"))
            for p in participants:
                part_list = list(MembersClub.objects.filter(id=p["member"]).values("id_User"))
                for d in part_list:
                    detail_list = list(User.objects.filter(id=d["id_User"]).values("id","first_name", "last_name",
                                                                                       "email", "height", "weight",
                                                                                       "age", "role", "gender",
                                                                                       "primary_sport",
                                                                                       "secondary_sport"))
                    for part in detail_list:
                        workout_list = list(Workout.objects.filter(owner=part["id"], event=event["id"])
                                                .values("name","description","latitude","longitude","radius",
                                                        "duration","distance","average_hr","calories_burned",
                                                        "average_speed","workout_effectiveness","heart_rate"
                                                        ))
                        if not workout_list:
                                work_detail = {
                                    "name": 0,
                                    "description": 0,
                                    "latitude": 0,
                                    "longitude": 0,
                                    "radius": 0,
                                    "duration": 0,
                                    "distance": 0,
                                    "average_hr": 0,
                                    "calories_burned": 0,
                                    "average_speed": 0,
                                    "workout_effectiveness": 0,
                                    "heart_rate": 0
                                }
                        else:
                                    work = workout_list[0]
                                    work_detail = {
                                    "name": work["name"],
                                    "description": work["description"],
                                    "latitude": work["latitude"],
                                    "longitude": work["longitude"],
                                    "radius": work["radius"],
                                    "duration": work["duration"],
                                    "distance": work["distance"],
                                    "calories_burned": work["calories_burned"],
                                    "average_speed": work["average_speed"],
                                    "workout_effectiveness": work["workout_effectiveness"],
                                    "heart_rate": work["heart_rate"]}
                    for part in detail_list:
                        if part["gender"] == User.MALE:
                            part["gender"] = "Male"
                        else:
                            part["gender"] = "Female"
                        participant = {"id":part["id"],
                                    "first_name": part["first_name"],
                                   "last_name": part["last_name"],
                                   "workout-details": work_detail
                                   }
                        participant_list.append(participant)
            if not participant_list:
                f_list.update({'participants_detail': participant_list})
            else:
                f_list.update({'participants_detail': participant_list})
            return JsonResponse(f_list, safe=False)
        except Events.DoesNotExist:
            return Response({'error': 'Event does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:
        pass


@csrf_exempt
@api_view(['PUT'])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def event_put(request, id_event):
    """Edit an event by id.
    The endpoint should be accessible by all authenticated Coaches
    """

    if request.method == "PUT":
        event = (get_object_or_404(Events, id=id_event))
        name = request.data.get('name')
        if name is None:
            return Response({"error": "Please provide a name."}, status=HTTP_400_BAD_REQUEST)
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
@permission_classes([IsAuthenticated, AthletePermission, ])
def workout_post(request):
    """ Register an athlete progress for the event.
    The endpoint should be accessible by all authenticated Athletes """

    if request.method == "POST":
        heart_rate = request.data.get('workout_effectiveness')
        if heart_rate == Workout.LOW:
            heart_rate = 1
        elif heart_rate == Workout.MED:
            heart_rate = 2
        elif heart_rate == Workout.HIGH:
            heart_rate = 3
        name = request.data.get('name')
        if name is None:
            name = ""
        description = request.data.get('description')
        if description is None:
            description = ""
        average_hr = request.data.get('average_hr')
        if average_hr is None:
            average_hr = 0
        workout = Workout(owner=request.user, name=name,
                          description=description,
                          event=Events.objects.get(id=request.data.get('event')),
                          latitude=1,
                          longitude=1, radius=1,
                          duration=request.data.get('duration'), distance=request.data.get('distance'),
                          average_hr=average_hr,
                          calories_burned=request.data.get('calories_burned'),
                          average_speed=request.data.get('average_speed'),
                          workout_effectiveness=heart_rate,
                          heart_rate=request.data.get('heart_rate'))
        workout.save()
        return Response(status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated, AthletePermission,))
def get_detail_workout(request):
    """ List workout history for an Athlete.
    The endpoint should be accessible by all authenticated Athletes """

    workout = list(
        Workout.objects.filter(owner=request.user).values("owner", "name", "event", "latitude", "longitude", "radius",
                                                          "duration", "distance", "average_hr", "calories_burned",
                                                          "average_speed", "workout_effectiveness", "heart_rate"))
    owner_detail = list()
    owner_detail.append(request.user.first_name)
    owner_detail.append(request.user.last_name)
    for w in workout:
        w["event"] = Events.objects.get(id=w["event"]).date
        w["owner"] = owner_detail
    if request.method == 'GET':
        return JsonResponse(workout, safe=False)


@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated, AdminPermission,))
def event_get_all_events(request):
    """Listing all events for admin.
    The endpoint should be accessible by Admin.
    """
    on_page = 4
    search = request.query_params.get('search')
    time = request.query_params.get('time')
    if time is not None:
        time = int(time)
    if time is None:
        events = Events.objects.all().values("id", "name", "description", "location", "date", "time")
    elif time == 1:
        today = date.today()
        events = Events.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day
                                       ).values("id", "name", "description", "location", "date", "time")
    elif time == 2:
        today = date.today()
        events = Events.objects.filter(date__year=today.year, date__month=today.month, date__day__gt=today.day
                                       ).values("id", "name", "description", "location", "date", "time")
    elif time == 3:
        today = date.today()
        events = Events.objects.filter(date__year=today.year, date__month=today.month, date__day__lt=today.day
                                       ).values("id", "name", "description", "location", "date", "time")
    if search is None:
        search = ""
    final_list = list()
    for event in events:
        if search.lower() in event['name'].lower():
            event_detail = {
                "id": event["id"],
                "name": event["name"],
                "description": event["description"],
                "location": event["location"],
                "date": event["date"],
                "time": event["time"]}
            participant_list = list()
            participants = list(Participants.objects.filter(event=event["id"], is_participant=True).values("member"))
            for p in participants:
                part_list = list(MembersClub.objects.filter(id=p["member"]).values("id_User"))
                for d in part_list:
                    detail_list = list(User.objects.filter(id=d["id_User"]).values("id", "first_name", "last_name",
                                                                                   "email", "height", "weight",
                                                                                   "age", "role", "gender",
                                                                                   "primary_sport",
                                                                                   "secondary_sport"))
                    for part in detail_list:
                        if part["gender"] == User.MALE:
                            part["gender"] = "Male"
                        else:
                            part["gender"] = "Female"
                        user = User.objects.get(id=d["id_User"])
                        participant = {"id": part["id"],
                                       "age": user.age,
                                       "gender": user.gender,
                                       "profile_image": user.profile_image,
                                       }
                        participant_list.append(participant)

            event_detail.update({'participants_detail': participant_list})
            final_list.append(event_detail)
    page = request.query_params.get('page')
    if page is not None:
        page = int(page)
        if page == 1:
            start = 0
        else:
            start = ((page-1) * (on_page-1)) + 1
        return Response({"events": final_list[start:start+on_page],
                        "page_number": ceil(len(final_list)/on_page)}, status=HTTP_200_OK)
    return Response(final_list, status=HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated, AllPermission,))
def has_events(request):
    memb = list(MembersClub.objects.filter(id_User=request.user))
    for m in memb:
        try:
            part = Participants.objects.filter(member=m, is_participant=True)
            return Response({"has_events": True}, status=HTTP_200_OK)
        except Participants.DoesNotExist:
            pass
    return Response({"has_events": False}, status=HTTP_200_OK)


