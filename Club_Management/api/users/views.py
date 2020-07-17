from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from users.models import User, UserManager
from users.serializers import UserSerializer
from django.core.mail import send_mail


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def reset_password(request):
    email = request.data.get("email")
    if email is None:
        return Response({'error': 'Please provide an email.'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'The email does not exist our database.'},
                        status=HTTP_404_NOT_FOUND)
    password = User.objects.make_random_password()
    user.set_password(password)
    user.save()
    message = ('Hello {}.\n'
               'This is an auto generated email.\n'
               'You requested that your password to be reset.\n'
               'Your new password is: {}\n'
               'You can login using the following link: {}\n'
               'Club Management team.').format(user.get_full_name(), password, 'http://127.0.0.1:8000/api/signin/')
    send_mail('Club Management New Password', message, 'test.club.django@gmail.com', [email], fail_silently=False,)
    return Response({'Success:': 'The email has been sent.'},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def invite(request):
    header = request.headers.get('Authorization')
    email = request.data.get("email")
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    if email is None:
        return Response({'error': 'Please provide an email.'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'},
                        status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role == 2:
        return Response({'error': 'Access denied.'})
    try:
        exist = User.objects.get(email=email)
        return Response({'error': 'The email is already used'},
                        status=HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass
    password = User.objects.make_random_password()
    newuser = User.objects.create_user(email=email, first_name='', last_name='', height=None, weight=None, password=password, role=2, age=18)
    newuser.save()
    message = ('Hello Mr/Mrs!\n'
               'You are invited  by {} to join Club Management.\n'
               'Your account was auto generated using your email.\n'
               'You can login using the following link: {}\n'
               'Login using the following credentials:\n'
               'email : {}\n'
               'password : {}\n'
               'Club Management team.').format(user.get_full_name(), 'http://127.0.0.1:8000/api/signin/', email, password)
    send_mail('Club Management Invite', message, 'test.club.django@gmail.com', [email], fail_silently=False, )
    return Response({'Success:': 'The email has been sent.'},
                    status=HTTP_200_OK)
