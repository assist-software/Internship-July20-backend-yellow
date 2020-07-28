from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from users.models import User
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.permissions import AdminORCoachPermission


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
    """
    This endpoint is used to signin.
    :param request:
    :return: token:,id:,role:
    """
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': "Invalid credentials."},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': "Token " + token.key,
                     'name': user.get_full_name(),
                     'id': user.id,
                     'role': user.role},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def reset_password(request):
    """
    This endpoint is used to reset the password of an user.
    :param request:
    :return: Response:
    """
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
               'Club Management team.').format(user.get_full_name(), password, 'http://192.168.1.4:8001/api/signin/')
    send_mail('Club Management New Password', message, 'test.club.django@gmail.com', [email], fail_silently=False, )
    return Response({'Success:': 'The email has been sent.'},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def invite(request):
    """
    This endpoint is used to invite an athlete by id
    :param request:
    :return: Response:
    """
    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    email = request.data.get("email")
    if email is None:
        return Response({'error': 'Please provide an email.'},
                        status=HTTP_400_BAD_REQUEST)
    user = User.objects.get(id=token.user_id)
    try:
        exist = User.objects.get(email=email)
        return Response({'error': 'The email is already used'},
                        status=HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass
    password = User.objects.make_random_password()
    new_user = User.objects.create_user(email=email, first_name='', last_name='', height=None, weight=None,
                                        password=password, role=User.ATHLETE, gender=User.MALE, age=18)
    new_user.save()
    message = ('Hello Mr/Mrs!\n'
               'You are invited  by {} to join Club Management.\n'
               'Your account was auto generated using your email.\n'
               'You can login using the following link: {}\n'
               'Login using the following credentials:\n'
               'email : {}\n'
               'password : {}\n'
               'Club Management team.').format(user.get_full_name(), 'http://192.168.1.4:8001/api/signin/',
                                               email, password)
    send_mail('Club Management Invite', message, 'test.club.django@gmail.com', [email], fail_silently=False, )
    return Response({'Success:': 'The email has been sent.'},
                    status=HTTP_200_OK)
