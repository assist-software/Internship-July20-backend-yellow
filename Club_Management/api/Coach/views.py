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
from api.permissions import AdminPermission, CoachPermission
from Club.models import Club
from django.core.paginator import Paginator


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((AdminPermission,))
def coach(request):
    # IF REQUEST IS POST
    if request.method == "POST":
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        if email is None:
            return Response({'error': 'Please provide an email.'},
                            status=HTTP_400_BAD_REQUEST)
        if first_name is None or last_name is None:
            return Response({'error': 'Please provide both first_name and last_name.'},
                            status=HTTP_400_BAD_REQUEST)
        try:
            exist = User.objects.get(email=email)
            return Response({'error': 'The email is already used'},
                            status=HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass
        password = User.objects.make_random_password()
        new_user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, height=None,
                                            weight=None, password=password, role=User.COACH, gender=User.MALE, age=18)
        new_user.save()
        message = ('Hello {}!\n'
                   'Your Coach profile at Club Management was created.\n'
                   'You can customize your profile at any time.\n'
                   'You can login using the following link: {}\n'
                   'Login using the following credentials:\n'
                   'email : {}\n'
                   'password : {}\n'
                   'Club Management team.').format(new_user.get_full_name(), 'http://127.0.0.1:8000/api/signin/', email,
                                                   password)
        send_mail('Club Management Coach Profile Created', message, 'test.club.django@gmail.com', [email],
                  fail_silently=False, )
        return Response({'name': new_user.get_full_name()},
                        status=HTTP_200_OK)
    else:  # IF REQUEST IS GET
        all_coaches = list(User.objects.filter(role=1).values("id", "first_name", "last_name", "email"))
        for i in range(len(all_coaches)):
            temp = all_coaches[i]
            clubs = list(Club.objects.filter(id_Owner=temp["id"]).values("name"))
            all_clubs = ""
            for j in range(len(clubs)):
                if j < 2:
                    t = clubs[j]
                    all_clubs = all_clubs + t["name"] + ", "
            all_clubs = all_clubs[:-2]
            if len(clubs)!=0:
                all_clubs = all_clubs + " + " + str(j - 1)
            temp["club"] = all_clubs
            all_coaches[i] = temp
        return Response({"coaches": all_coaches}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["DELETE", "PUT", "GET"])
@permission_classes((AdminPermission, CoachPermission))
def delete_edit(request: {}, id: int) -> Response:
    """
    This endpoint is used to delete, edit or get a coach by ID
    Can be accessed by ADMINS AND COACHES
     """
    header = request.headers.get('Authorization')
    token = Token.objects.get(key=header)
    user = User.objects.get(id=token.user_id)

    # IF METHOD IS GET
    if request.method == "GET":
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
        if user.role != User.ADMIN:
            return Response({'error': 'Access denied.'})
        try:
            coach = User.objects.get(id=id)
            coach.delete()
            return Response({'success': 'The coach was removed.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:  # IF METHOD IS PUT
        if user.role != User.COACH:
            return Response({'error': 'Access denied.'})
        try:
            coach = User.objects.get(id=id)
            if token.user_id != id:
                return Response({'error': 'Coaches can only edit themselves.'}, status=HTTP_400_BAD_REQUEST)
            first_name = request.data.get('name')
            last_name = request.data.get('name')
            email = request.data.get("email")
            if email is None:
                return Response({'error': 'Please provide an email.'},
                                status=HTTP_400_BAD_REQUEST)
            if first_name == "":
                return Response({'error': 'Please provide a name.'},
                                status=HTTP_400_BAD_REQUEST)
            if last_name == "":
                return Response({'error': 'Please provide a name.'},
                                status=HTTP_400_BAD_REQUEST)
            coach.first_name = first_name
            coach.last_name = last_name
            coach.email = email
            coach.save()
            return Response({'success': 'The coach was edited.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
