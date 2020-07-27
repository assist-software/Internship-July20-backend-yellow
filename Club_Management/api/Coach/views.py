from math import ceil

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response

from api.Coach.serializers import CoachSerializer
from users.models import User
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from api.permissions import AdminPermission, AdminORCoachPermission
from Club.models import Club
from django.db.models import Q


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((IsAuthenticated, AdminPermission, ))
def coach(request: {}) -> Response:
    """
        This endpoint is used to create a new coach if the request method is POST.
        And if the request method is GET it returns a list of all coaches.
        Can be accessed by ADMINS.
    """
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
        search = request.query_params.get('search')
        if search is None:
            search = ""
        all_coaches = User.objects.filter(role=1).values("id", "first_name", "last_name", "email")
        final = list()
        for coach in all_coaches:
            user = User.objects.get(id=coach["id"])
            if search.lower() in user.get_full_name().lower():
                clubs = Club.objects.filter(id_Owner=coach["id"]).values("name")
                all_clubs = ""
                for j in range(len(clubs)):
                    if j < 2:
                        t = clubs[j]
                        all_clubs = all_clubs + t["name"] + ", "
                all_clubs = all_clubs[:-2]
                if len(clubs) != 0 and j != 0:
                    all_clubs = all_clubs + " + " + str(j - 1)
                coach["club"] = all_clubs
                final.append(coach)
        page = request.query_params.get('page')
        on_page = 6
        coaches = CoachSerializer(final, many=True)
        if page is not None:
            page = int(page)
            if page == 1:
                start = 0
            else:
                start = ((page - 1) * (on_page - 1)) + 1
            return Response({"coaches": coaches.data[start:start+on_page],
                             "page_number": ceil(len(coaches.data)/on_page)}, status=HTTP_200_OK)
        else:
            return JsonResponse({"coaches": coaches.data}, safe=False, status=HTTP_200_OK)


@csrf_exempt
@api_view(["DELETE", "PUT", "GET"])
@permission_classes((IsAuthenticated, AdminORCoachPermission, ))
def delete_edit(request: {}, id: int) -> Response:
    """
    This endpoint is used to delete, edit or get a coach by ID
    Can be accessed by ADMINS AND COACHES
    """

    # IF METHOD IS GET
    if request.method == "GET":
        try:
            coach = User.objects.get(id=id, role=1)
            clubs = Club.objects.filter(id_Owner=coach.id).values("name")
            all_clubs = ""
            for j in range(len(clubs)):
                if j < 2:
                    t = clubs[j]
                    all_clubs = all_clubs + t["name"] + ", "
            all_clubs = all_clubs[:-2]
            if len(clubs) != 0 and j != 0:
                all_clubs = all_clubs + " + " + str(j - 1)
            coach_to_be_serialized = {"id": coach.id, "first_name": coach.first_name,
                                      "last_name": coach.last_name, "email": coach.email, "club": all_clubs}
            question = CoachSerializer(coach_to_be_serialized)
            return Response(question.data, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
    # IF METHOD IS DELETE
    if request.method == "DELETE":
        if request.user.role != User.ADMIN:
            return Response({'error': 'Access denied.'})
        try:
            coach = User.objects.get(id=id)
            clubs = Club.objectes.filter(id_Owner=coach)
            for club in clubs:
                club.id_Owner = request.user
            coach.delete()
            return Response({'success': 'The coach was removed.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Coach does not exist.'}, status=HTTP_404_NOT_FOUND)
    else:  # IF METHOD IS PUT
        try:
            coach = User.objects.get(id=id)
            if request.user.id != id:
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
