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
from users.models import User
from django.core.mail import send_mail
from django.http import JsonResponse


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((AllowAny,))
def coach(request):
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role != 0:
        return Response({'error': 'Access denied.'})

    # IF REQUEST IS POST
    if request.method == "POST":
        name = str(request.data.get('name'))
        email = request.data.get("email")
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
                                           weight=None, password=password, role=1, age=18)
        newuser.save()
        message = ('Hello {}!\n'
                   'Your Coach profile at Club Management was created.\n'
                   'You can customize your profile at any time.\n'
                   'You can login using the following link: {}\n'
                   'Login using the following credentials:\n'
                   'email : {}\n'
                   'password : {}\n'
                   'Club Management team.').format(newuser.get_full_name(), 'http://127.0.0.1:8000/api/signin/', email,
                                                   password)
        send_mail('Club Management Coach Profile Created', message, 'test.club.django@gmail.com', [email],
                  fail_silently=False, )
        return Response({'Success:': 'The email has been sent.'},
                        status=HTTP_200_OK)
    else:  # IF REQUEST IS GET
        all_coaches = list(User.objects.filter(role=1).values("id", "first_name", "last_name", "email"))
        return Response({"success": all_coaches}, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
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

    name = request.headers.get('name')


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
        return Response({'error': 'Invalid Token'}, status=HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)

    # IF METHOD IS GET
    if request.method == "GET":
        if user.role == 2:
            return Response({'error': 'Access denied.'})
        try:
            coach = User.objects.get(id=id, role=1)
            return Response({'first_name': coach.first_name,
                             'last_name': coach.last_name,
                             'email': coach.email,
                             }, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
    # IF METHOD IS DELETE
    if request.method == "DELETE":
        if user.role != 0:
            return Response({'error': 'Access denied.'})
        try:
            coach = User.objects.get(id=id)
            coach.delete()
            return Response({'success': 'The coach was removed.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:  # IF METHOD IS PUT
        if user.role != 1:
            return Response({'error': 'Access denied.'})
        try:
            coach = User.objects.get(id=id)
            if token.user_id != id:
                return Response({'error': 'Coaches can only edit themselves.'}, status=HTTP_400_BAD_REQUEST)
            name = str(request.data.get('name'))
            email = request.data.get("email")
            if email is None:
                return Response({'error': 'Please provide an email.'},
                                status=HTTP_400_BAD_REQUEST)
            if name == "":
                return Response({'error': 'Please provide a name.'},
                                status=HTTP_400_BAD_REQUEST)
            name = name.split()
            if len(name) < 2:
                name.append("")
            coach.first_name = name[0]
            coach.last_name = name[1]
            coach.email = email
            coach.save()
            return Response({'success': 'The coach was edited.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
