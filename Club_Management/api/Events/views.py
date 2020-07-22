from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from django.views.decorators.csrf import csrf_exempt
from Events.models import Events, Participants, Workout
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from users.models import User
from Club.models import Club
from Athletes.models import Sports
from Club.models import MembersClub


from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from Events.serializers import EventsSerializer


@csrf_exempt
@api_view(['POST'])
def event_post(request):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role == 2:
        return Response({'error': 'Access denied.'})

    if request.method == "POST":
        # import ipdb
        # ipdb.set_trace()
        event = Events(club_id=Club.objects.get(name=request.data.get('club')), name=request.data.get('name'), description=request.data.get('description'),
                       location=request.data.get('location'), date=request.data.get('date'),
                       time=request.data.get('time'), sport_id=Sports.objects.get(description=request.data.get('sport')))
        event.save()
        serializers = EventsSerializer(data=event.__dict__)
        if serializers.is_valid():
            print("Serializers data  {}".format(serializers.data))
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def event_join(request, id_event):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role != 2:
        return Response({'error': 'Access denied.'})

    ev = Events.objects.get(id=id_event)
    try:
        mem_cl = MembersClub.objects.get(id_club=ev.club_id, id_User=user)
        if mem_cl.id_User == user:
            new_request = Participants(event=ev, member=mem_cl, is_invited=False,
                                       is_requested=True, is_participant=False)
            new_request.save()
            serializers = EventsSerializer(data=new_request.__dict__)
            if serializers.is_valid():
                return Response(status=status.HTTP_202_ACCEPTED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except MembersClub.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)




@csrf_exempt
@api_view(['GET'])
def event_get(request):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role != 2:
        return Response({'error': 'Access denied.'})

    clubs = list(MembersClub.objects.filter(id_User=user).values("id_club"))
    print(clubs)
    final_list= list()
    for club in clubs:
        ev=list(Events.objects.filter(club_id=club["id_club"]).values("name","description","location","date","time","sport_id"))
        for i in ev:
            i["sport_id"] = Sports.objects.get(id=i["sport_id"]).description
        final_list.append(ev)

    if request.method == 'GET':

        return JsonResponse(final_list, safe=False)



@csrf_exempt
@api_view(['DELETE'])
@permission_classes((AllowAny,))
def event_delete(request, id_event):

    header = request.headers.get('Authorization')
    if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role !=1:
        return Response({'error': 'Access denied.'})

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
@permission_classes((AllowAny,))
def event_get_detail(request, id_event):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role != 1:
        return Response({'error': 'Access denied.'})

    if request.method == "GET":
        try:
            event = Events.objects.get(id=id_event)
            return Response({"name": event.name,
                             "description": event.description,
                             "location": event.location,
                             "date":event.date,
                             "time":event.time,
                             "sport_id":event.sport_id
                             })
        except Events.DoesNotExist:
            return Response({'error': 'Event does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:
        pass


@csrf_exempt
@api_view(['PUT'])
@permission_classes((AllowAny,))
def event_put(request, id_event):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role != 1:
        return Response({'error': 'Access denied.'})

    if request.method == "PUT":

        header = request.headers.get('Authorization')
        if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=token.user_id)
        if user.role == 2 or user.role == 0:
            return Response({'error': 'Access denied.'})

        event = (get_object_or_404(Events, id=id_event))
        event.club_id = Club.objects.get(name=request.data.get('club'))
        event.name = request.data.get('name')
        event.description = request.data.get('description')
        event.location = request.data.get('location')
        event.date = request.data.get('date')
        event.time= request.data.get('time')
        event.sport_id= Sports.objects.get(description=request.data.get('sport'))

        event.save()
        return Response(status=HTTP_200_OK)

# workout
@csrf_exempt
@api_view(['POST'])
def workout_post(request):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role != 2:
        return Response({'error': 'Access denied.'})

    if request.method == "POST":
        # import ipdb
        # ipdb.set_trace()
        workout = Workout(owner=user, name=request.data.get('name'), description=request.data.get('description'),
                          event=Events.objects.get(name=request.data.get('event')),
                          latitude=request.data.get('latitude'),
                          longitude=request.data.get('longitude'), radius=request.data.get('radius'),
                          duration=request.data.get('duration'),distance=request.data.get('distance'),
                          average_hr=request.data.get('average_hr'),calories_burned=request.data.get('calories_burned'),
                          average_speed=request.data.get('average_speed'),
                          workout_effectiveness=request.data.get('workout_effectiveness'),
                          heart_rate=request.data.get('heart_rate'))
        workout.save()
        serializers = EventsSerializer(data=workout.__dict__)
        if serializers.is_valid():
            print("Serializers data  {}".format(serializers.data))
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

