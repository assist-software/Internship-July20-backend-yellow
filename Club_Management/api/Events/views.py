from datetime import date
from math import ceil
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from Events.models import Events, Participants, Workout
from rest_framework.response import Response
from users.models import User
from Club.models import Club
from Athletes.models import Sports
from Club.models import MembersClub
from django.views.decorators.csrf import csrf_exempt
from Events.serializers import EventsSerializer
from rest_framework.permissions import IsAuthenticated
from api.permissions import AdminORCoachPermission, AthletePermission, CoachPermission, AdminPermission, AllPermission
from Events.models import Workout
from api.Coach.views import pagination


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
            return Response({"error": "Name already exists!"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist:
            event = Events(club_id=club, name=name,
                           description=description,
                           location=location, date=date,
                           time=time, )
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
        events = list(Events.objects.filter(club_id=club["id_club"]).values("id", "club_id", "name", "location",
                                                                            "date"))
        for event in events:
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

    try:
        event = Events.objects.get(id=id_event)
        event.delete()
        return Response({'success': 'The event was removed.'}, status=HTTP_200_OK)
    except Events.DoesNotExist:
        return Response({'error': 'Event does not exist.'}, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated, AllPermission))
def event_get_detail(request, id_event):
    """ Get event info and a list of athletes that have
    requested to join the event.
    The endpoint should be accessible by all authenticated Coaches."""
    try:
        events = list(Events.objects.filter(id=id_event).values("id", "name", "description", "location",
                                                                "date", "time", "sport_id"))
        event = events[0]
        detail_list_event = {
            "id": id_event,
            "name": event["name"],
            "description": event["description"],
            "location": event["location"],
            "date": event["date"],
            "time": event["time"]}
        participants_list = list()
        participants = list(Participants.objects.filter(event=event["id"], is_participant=True).values("member"))
        for participant in participants:
            part_list = list(MembersClub.objects.filter(id=participant["member"]).values("id_User"))
            for d in part_list:
                detail_list = list(User.objects.filter(id=d["id_User"]).values("id", "first_name", "last_name",
                                                                               "email", "height", "weight",
                                                                               "age", "role", "gender",
                                                                               "primary_sport",
                                                                               "secondary_sport"))
                for part in detail_list:
                    workout_list = list(Workout.objects.filter(owner=part["id"], event=event["id"])
                                        .values("name", "description", "latitude", "longitude", "radius",
                                                "duration", "distance", "average_hr", "calories_burned",
                                                "average_speed", "workout_effectiveness", "heart_rate"
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
                    participant_detail = {"id": part["id"],
                                          "first_name": part["first_name"],
                                          "last_name": part["last_name"],
                                          "workout-details": work_detail
                                          }
                    participants_list.append(participant_detail)

        detail_list_event.update({'participants_detail': participants_list})

        return JsonResponse(detail_list_event, safe=False)
    except Events.DoesNotExist:
        return Response({'error': 'Event does not exist.'}, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['PUT'])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def event_put(request, id_event):
    """Edit an event by id.
    The endpoint should be accessible by all authenticated Coaches
    """

    event = (get_object_or_404(Events, id=id_event))
    name = request.data.get('name')
    if name is None:
        return Response({"error": "Please provide a name."}, status=HTTP_400_BAD_REQUEST)
    club = request.data.get('club')
    if club is None:
        return Response({"error": "Please provide a club."}, status=HTTP_400_BAD_REQUEST)
    description = request.data.get('description')
    if description is None:
        return Response({"error": "Please provide a description."}, status=HTTP_400_BAD_REQUEST)
    location = request.data.get('location')
    if location is None:
        return Response({"error": "Please provide a location."}, status=HTTP_400_BAD_REQUEST)
    date = request.data.get('date')
    if date is None:
        return Response({"error": "Please provide a date."}, status=HTTP_400_BAD_REQUEST)
    time = request.data.get('time')
    if time is None:
        return Response({"error": "Please provide a time."}, status=HTTP_400_BAD_REQUEST)
    event.club_id = (get_object_or_404(Club, name=club))
    event.name = name
    event.description = description
    event.location = location
    event.date = date
    event.time = time
    event.save()
    return Response(status=HTTP_200_OK)


# workout
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, AthletePermission, ])
def workout_post(request):
    """ Register an athlete progress for the event.
    The endpoint should be accessible by all authenticated Athletes """

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

    workouts = list(
        Workout.objects.filter(owner=request.user).values("owner", "name", "event", "latitude", "longitude", "radius",
                                                          "duration", "distance", "average_hr", "calories_burned",
                                                          "average_speed", "workout_effectiveness", "heart_rate"))
    owner_detail = list()
    owner_detail.append(request.user.first_name)
    owner_detail.append(request.user.last_name)
    for workout in workouts:
        workout["event"] = Events.objects.get(id=workout["event"]).date
        workout["owner"] = owner_detail
    if request.method == 'GET':
        return JsonResponse(workouts, safe=False)


@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def event_get_all_events(request):
    """Listing all events for admin.
    The endpoint should be accessible by Admin.
    """
    search = request.query_params.get('search')
    time = request.query_params.get('time')
    """
    TIME
    --------------------------------
    None = Mobile request
    1 = Ongoing (the current day)
    2 = Future (>current day)
    3 = Past (<current day)
    --------------------------------
    """
    if time is not None:
        time = int(time)
    today = date.today()
    if time is None:
        if request.user.role == User.COACH:
            clubs = Club.objects.filter(id_Owner=request.user)
            events = list()
            for club in clubs:
                events_temp = Events.objects.filter(club_id=club).values("id", "name", "description", "location",
                                                                         "date", "time")
                events.append(events_temp)
        else:
            events = Events.objects.all().values("id", "name", "description", "location", "date", "time")
    elif time == 1:
        if request.user.role == User.COACH:
            clubs = Club.objects.filter(id_Owner=request.user)
            events = list()
            for club in clubs:
                events_temp = Events.objects.filter(club_id=club, date__year=today.year, date__month=today.month,
                                                    date__day=today.day).values("id", "name", "description",
                                                                                "location", "date", "time")
                events.append(events_temp)
        else:
            events = Events.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day
                                           ).values("id", "name", "description", "location", "date", "time")
    elif time == 2:
        if request.user.role == User.COACH:
            clubs = Club.objects.filter(id_Owner=request.user)
            events = list()
            for club in clubs:
                events_temp = Events.objects.filter(club_id=club, date__year=today.year, date__month=today.month,
                                                    date__day__gt=today.day).values("id", "name", "description",
                                                                                    "location", "date", "time")
                events.append(events_temp)
        else:
            events = Events.objects.filter(date__year=today.year, date__month=today.month, date__day__gt=today.day
                                           ).values("id", "name", "description", "location", "date", "time")
    elif time == 3:
        if request.user.role == User.COACH:
            clubs = Club.objects.filter(id_Owner=request.user)
            events = list()
            for club in clubs:
                events_temp = Events.objects.filter(club_id=club, date__year=today.year, date__month=today.month,
                                                    date__day__lt=today.day).values("id", "name", "description",
                                                                                    "location", "date", "time")
                events.append(events_temp)
        else:
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
    pg = request.query_params.get('page')
    on_page = 4
    if pg is not None:
        start, end = pagination(on_page=on_page, page=pg)
        return Response({"events": final_list[start:end],
                         "page_number": ceil(len(final_list) / on_page)}, status=HTTP_200_OK)
    else:
        return Response(final_list, status=HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated, AllPermission,))
def has_events(request):
    """Check if an user is a member of at least one event"""
    clubs = MembersClub.objects.filter(id_User=request.user, is_member=True).values("id", "id_club")
    for club in clubs:
        events = Events.objects.filter(club_id=club["id_club"]).values("id")
        for event in events:
            part = Participants.objects.filter(event=event["id"], member=club["id"], is_participant=True)
            if part:
                return Response({"has_events": True}, status=HTTP_200_OK)
    return Response({"has_events": False}, status=HTTP_200_OK)
