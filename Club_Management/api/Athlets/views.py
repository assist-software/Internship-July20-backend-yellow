from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.contrib.auth.forms import UserChangeForm
from Athletes.serializers import AthleteSerializer
from rest_framework.response import Response
from users.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from Athletes.models import Sports


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((AllowAny,))
class AthletViewSet(viewsets.ModelViewSet):
    queryset = AthleteSerializer()
    serializer_class = AthleteSerializer


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((AllowAny,))
def athlete(request):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user_auth = User.objects.get(id=token.user_id)
    if request.method == "POST":
        if user_auth.role == 2:
            return Response({"error": "Access denied"},)
        name = str(request.data.get('name'))
        if name is None:
            return Response({"error": "Please provide an email."}, status=HTTP_400_BAD_REQUEST)
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            return Response({"error": "Email is already used."}, status=HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass
        name = name.split()
        if len(name) < 2:
            name.append("")
        password = User.objects.make_random_password()
        newuser = User.objects.create_user(email=email, first_name=name[0], last_name=name[1], height=None,
                                           weight=None, password=password, role=2, age=18)
        newuser.save()
        message = ('Hello {}!\n'
                   'Your Athlete profile at Club Management was created.\n'
                   'You can customize your profile at any time.\n'
                   'You can login using the following link: {}\n'
                   'Login using the following credentials:\n'
                   'email : {}\n'
                   'password : {}\n'
                   'Club Management team.').format(newuser.get_full_name(), 'http://127.0.0.1:8000/api/signin/', email,
                                                   password)
        send_mail('Club Management Athlete Profile Created', message, 'test.club.django@gmail.com', [email],
                  fail_silently=False, )
        return Response({'Success:': 'The email has been sent.'},
                        status=HTTP_200_OK)
        return Response({'Success:': 'The athlete was created'},
                        status=HTTP_200_OK)
    else:
        if user_auth.role != 0:
            return Response({"error": "Access denied"})
        all_athletes = list(User.objects.filter(role=2).values("id", "first_name", "last_name", "age", "height", "weight",
                                                               "primary_sport", "secondary_sport",))
        return Response({"Athletes": all_athletes}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["DELETE", "PUT", "GET"])
@permission_classes((AllowAny,))
def delete_edit(request, id):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token   '}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)

    # IF METHOD IS DELETE
    if request.method == "DELETE":
        if user.role != 0:
            return Response({'error': 'Access denied.'})
        try:
            athlete = User.objects.get(id=id)
            athlete.delete()
            return Response({'success': 'The athlete was removed.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Athlete does not exist.'}, status=HTTP_404_NOT_FOUND)
    if request.method == "GET":
        if user.role != 0:
            return Response({'error': 'Access denied.'})
        atl = User.objects.get(id=id)
        return Response({"id": atl.id,
                        "first_name": atl.first_name,
                        "last_name": atl.last_name,
                        "email": atl.email,
                        "age": atl.age,
                         "height": atl.height,
                         "weight": atl.weight,
                        "primary_sport": atl.primary_sport,
                         "secondary_sport": atl.secondary_sport}, status=HTTP_200_OK)
    if request.method == "PUT":
        if id != user.id :
            return Response({'error': 'Access denied.'})
        name = str(request.data.get("name"))
        name = name.split()
        if len(name) < 2:
            name.append("")
        if name is None:
            return Response({"error": "Please provide a name"}, status=HTTP_400_BAD_REQUEST)
        age = request.data.get("age")
        if age is None:
            return Response({"error": "Please provide an age"}, status=HTTP_400_BAD_REQUEST)
        primary_sport = request.data.get("primary_sport")
        if primary_sport is None:
            return Response({"error": "Please provide a primary sport"}, status=HTTP_400_BAD_REQUEST)
        secondary_sport = request.data.get("secondary_sport")
        if secondary_sport is None:
            return Response({"error": "Please provide a secondary sport"}, status=HTTP_400_BAD_REQUEST)
        height = request.data.get("height")
        if height is None:
            return Response({"error": "Please provide a height"}, status=HTTP_400_BAD_REQUEST)
        weight = request.data.get("weight")
        if weight is None:
            return Response({"error": "Please provide a weight"}, status=HTTP_400_BAD_REQUEST)
        '''
        gen = request.data.get("gen")
        if gen is None:
            return Response({"error": "Please provide a gender"}, status=HTTP_400_BAD_REQUEST)
        '''
        user.first_name = name[0]
        user.last_name = name[1]
        user.age = age
        user.primary_sport = Sports.objects.get(description=primary_sport)
        user.secondary_sport = Sports.objects.get(description=secondary_sport)
        user.height = height
        user.weight = weight
        user.save()
        return  Response({'Success': "Athlete was modified"}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
    name = str(request.data.get("name"))
    email = request.data.get("email")
    try:
        exist = User.objects.get(email=email)
        return Response({"error": "Email is already used."},status=HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        password = request.data.get("password")
        name = name.split()
        if len(name) < 2:
            name.append("")
        newuser = User.objects.create_user(email=email, first_name=name[0], last_name=name[1], height=None,
                                           weight=None, password=password, role=2, age=18)
        newuser.save()
        return Response({"success": "User was created"},status=HTTP_200_OK)