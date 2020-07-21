'''
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST

from .serializers import AthleteSerializer
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
@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((AllowAny,))



class AthletViewSet(viewsets.ModelViewSet):
    queryset = AthleteSerializer()
    serializer_class = AthleteSerializer

def athlete(request):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user=User.objects.get()
    if user.role != 0:
        return Response({'error': 'Access denied.'})
    if request.method=='POST':
        name=str(request.data.get('name'))
        email=request.data.get('email')
        if email is None:
            return Response({'error': 'Please provide an email.'},
                            status=HTTP_400_BAD_REQUEST)
        if name == "":
            return Response({'error': 'Please provide a name.'},
                            status=HTTP_400_BAD_REQUEST)
        try:
            exist = User.objects.get(email=email)
            return Response({'error': 'The email is already used'},
                            status=HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass
        name = name.split()
        if len(name) < 2:
            name.append("")
        password = User.objects.make_random_password()
        newuser = User.objects.create_user(email=email, first_name=name[0], last_name=name[1], height=None,
                                           weight=None, password=password, role=2, age=20)
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
    else:
        all_athletes = list(User.objects.filter(role=2).values())


'''