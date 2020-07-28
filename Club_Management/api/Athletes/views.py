from math import ceil

from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from users.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from Athletes.models import Sports
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.permissions import AdminORCoachPermission, AllPermission
from Club.models import Club, MembersClub
from Athletes.serializers import SportSerializer, AthleteSerializer


@swagger_auto_schema(method='get',
                     operation_description="This endpoint is used to create a new athlete if the request method is "
                                           "POST.And if the request method is GET it returns a list of all "
                                           "athletes.Can be accessed by ADMINS or COACHES.",
                     responses={200: AthleteSerializer,
                                400: "Bad request"})
@swagger_auto_schema(methods=['post'],
                     operation_description="Creating an athlete: The ADMIN will be able to create an athlete.",
                     request_body=AthleteSerializer,
                     responses={200: 'Success : The athlete was created',
                                400: "Bad request"})
@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def athlete(request):
    """
            This endpoint is used to create a new athlete if the request method is POST.
            And if the request method is GET it returns a list of all athletes.
            Can be accessed by ADMINS or COACHES.
    """
    if request.method == "POST":
        name = str(request.data.get('name'))
        if name is None:
            return Response({"error": "Please provide a name."}, status=HTTP_400_BAD_REQUEST)
        email = request.data.get("email")
        if email is None:
            return Response({"error": "Please provide an email."}, status=HTTP_400_BAD_REQUEST)
        primary_sport = request.data.get('primary_sport')
        if primary_sport is None:
            primary_sport = None
        else:
            primary_sport = Sports.objects.get(description=primary_sport)
        secondary_sport = request.data.get('secondary_sport')
        if secondary_sport is None:
            secondary_sport = None
        else:
            secondary_sport = Sports.objects.get(description=secondary_sport)
        gender = request.data.get('gender')
        if gender is None:
            return Response({"error": "Please provide a gender."}, status=HTTP_400_BAD_REQUEST)
        if gender == 'M' or gender == "Male":
            gender = User.MALE
        elif gender == 'F' or gender == "Female":
            gender = User.FEMALE
        age = request.data.get('age')
        if age is None:
            return Response({"error": "Please provide an age"}, status=HTTP_400_BAD_REQUEST)
        height = request.data.get('height')
        if height is None:
            return Response({"error": "Please provide a height"}, status=HTTP_400_BAD_REQUEST)
        weight = request.data.get('weight')
        if weight is None:
            return Response({"error": "Please provide a weight"}, status=HTTP_400_BAD_REQUEST)
        profile_image = request.data.get('profile_image')
        try:
            user = User.objects.get(email=email)
            return Response({"error": "Email is already used."}, status=HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass
        name = name.split()
        if len(name) < 2:
            name.append("")
        password = User.objects.make_random_password()
        new_user = User.objects.create_user(email=email, first_name=name[0], last_name=name[1],
                                            height=height, weight=weight, password=password,
                                            role=2, gender=gender, age=age,
                                            primary_sport=primary_sport, secondary_sport=secondary_sport,
                                            profile_image=profile_image)
        new_user.save()
        club = request.data.get('club')
        clubs = Club.objects.all()
        for cb in clubs:
            if club is not None and cb["name"] == club:
                non_member = MembersClub(id_User=new_user, id_club=cb, is_invited=False, is_requested=False,
                                         is_member=True)
            else:
                non_member = MembersClub(id_User=new_user, id_club=cb, is_invited=False, is_requested=False,
                                        is_member=False)
            non_member.save()
        message = ('Hello {}!\n'
                   'Your Athlete profile at Club Management was created.\n'
                   'You can customize your profile at any time.\n'
                   'You can login using the following link: {}\n'
                   'Login using the following credentials:\n'
                   'email : {}\n'
                   'password : {}\n'
                   'Club Management team.').format(new_user.get_full_name(), 'http://192.168.149.50:8001/api/signin/',
                                                   email, password)
        send_mail('Club Management Athlete Profile Created', message, 'test.club.django@gmail.com', [email],
                  fail_silently=False, )
        return Response({'Success:': 'The athlete was created'},
                        status=HTTP_200_OK)
    else:  # IF REQUEST METHOD IS GET
        search = request.query_params.get('search')
        if search is None:
            search = ""
        on_page = 9
        all_athletes = User.objects.filter(role=2).values("id", "first_name", "last_name", "age",
                                                          "height", "weight", "gender", "email",
                                                          "primary_sport", "secondary_sport", )
        final = list()
        for a in all_athletes:
            if search.lower() in (a["first_name"] + " " + a["last_name"]).lower():
                try:
                    a["primary_sport"] = Sports.objects.get(id=a["primary_sport"]).description
                except Sports.DoesNotExist:
                    pass
                try:
                    a["secondary_sport"] = Sports.objects.get(id=a["secondary_sport"]).description
                except Sports.DoesNotExist:
                    pass
                if a["gender"] == User.MALE:
                    a["gender"] = "Male"
                else:
                    a["gender"] = "Female"
                final.append(a)
        athletes = AthleteSerializer(final, many=True)
        page = request.query_params.get('page')
        if page is not None:
            page = int(page)
            if page == 1:
                start = 0
            else:
                start = ((page - 1) * (on_page - 1)) + 1
            return JsonResponse({"athletes": athletes.data[start:start+on_page],
                                "page_number": ceil(len(athletes.data)/on_page)}, safe=False, status=HTTP_200_OK)
        else:
            return JsonResponse({"athletes": athletes.data}, safe=False, status=HTTP_200_OK)


@swagger_auto_schema(method='get',
                     operation_description="This endpoint is used to create a new athlete if the request method is "
                                           "POST.And if the request method is GET it returns a list of all "
                                           "athletes.Can be accessed by ADMINS or COACHES.",
                     responses={200: AthleteSerializer,
                                400: "Bad request"})
@swagger_auto_schema(methods=['put'],
                     operation_description="Creating an athlete: The ADMIN will be able to create an athlete.",
                     request_body=AthleteSerializer,
                     responses={200: 'success : The athlete has been modified.',
                                404: "Bad request"})
@swagger_auto_schema(methods=['delete'],
                     operation_description="Deleting an athlete: The ADMIN will be able to delete an athlete.",
                     responses={200: 'success : The athlete was removed.',
                                404: "Bad request"})
@csrf_exempt
@api_view(["DELETE", "PUT", "GET"])
@permission_classes((IsAuthenticated, AllPermission,))
def delete_edit(request, id):
    """
            This endpoint is used to delete, edit or get an athlete by ID.
            Can be accessed by ALL Users.
    """
    # IF METHOD IS DELETE
    if request.method == "DELETE":
        if request.user.role != User.ADMIN:
            return Response({'error': 'Access denied.'})
        try:
            athlete = User.objects.get(id=id)
            athlete.delete()
            return Response({'success': 'The athlete was removed.'}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Athlete does not exist.'}, status=HTTP_404_NOT_FOUND)
    if request.method == "GET":
        try:
            atl = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)
        atl_to_be_serialized = {"id": atl.id,
                                "first_name": atl.first_name,
                                "last_name": atl.last_name,
                                "email": atl.email,
                                "age": atl.age,
                                "gender": User.GENDERS[atl.gender][atl.gender],
                                "height": atl.height,
                                "weight": atl.weight,
                                "primary_sport": atl.primary_sport.description,
                                "secondary_sport": atl.secondary_sport.description}
        atl_ser = AthleteSerializer(atl_to_be_serialized)
        return JsonResponse(atl_ser.data, safe=False, status=HTTP_200_OK)
    if request.method == "PUT":
        if id != request.user.id:
            return Response({'error': 'Access denied.'})
        name = str(request.data.get("name"))
        name = name.split()
        if request.user.role == User.ATHLETE:
            pass
        else:
            if len(name) < 2:
                name.append("")
            request.user.first_name = name[0]
            request.user.last_name = name[1]
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
        gender = request.data.get("gender")
        if gender is None:
            pass
        else:
            if gender == 'M':
                request.user.gender = User.MALE
            elif gender == 'F':
                request.user.gender = User.FEMALE
        image = request.data.get('avatar')
        if image is None:
            pass
        else:
            request.user.profile_image = image
        request.user.age = age
        request.user.primary_sport = Sports.objects.get(description=primary_sport)
        request.user.secondary_sport = Sports.objects.get(description=secondary_sport)
        request.user.height = height
        request.user.weight = weight
        request.user.save()
        return Response({'Success': "Athlete was modified"}, status=HTTP_200_OK)


param1 = openapi.Parameter('first name', openapi.IN_QUERY, description="first name", type=openapi.TYPE_STRING)
param2 = openapi.Parameter('last name', openapi.IN_QUERY, description="last name", type=openapi.TYPE_STRING)
param3 = openapi.Parameter('email', openapi.IN_QUERY, description="email", type=openapi.TYPE_STRING)
param4 = openapi.Parameter('password', openapi.IN_QUERY, description="password", type=openapi.TYPE_STRING)


@swagger_auto_schema(methods=['post'],
                     operation_description="Creating an athlete: The ADMIN will be able to create an athlete.",
                     manual_parameters=[param1, param2, param3, param4],
                     responses={200: 'Success : User was created',
                                400: "Bad request"})
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
    first_name = request.data.get("first_name")
    if first_name is None:
        return Response({"error": "Please provide a  first name."}, status=HTTP_400_BAD_REQUEST)
    last_name = request.data.get("last_name")
    if last_name is None:
        return Response({"error": "Please provide a last name."}, status=HTTP_400_BAD_REQUEST)
    email = request.data.get("email")
    if email is None:
        return Response({"error": "Please provide an email."}, status=HTTP_400_BAD_REQUEST)
    try:
        exist = User.objects.get(email=email)
        return Response({"error": "Email is already used."}, status=HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        password = request.data.get("password")
        new_user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, height=None,
                                            weight=None, password=password, role=User.ATHLETE, gender=User.MALE,
                                            age=0, primary_sport=Sports.objects.get(id=1),
                                            secondary_sport=Sports.objects.get(id=2))
        new_user.save()
        clubs = Club.objects.all()
        for cb in clubs:
            non_member = MembersClub(id_User=new_user, id_club=cb, is_invited=False, is_requested=False,
                                     is_member=False)
            non_member.save()
        return Response({"success": "User was created"}, status=HTTP_200_OK)


@swagger_auto_schema(method='get',
                     operation_description="This endpoint is used to create a new athlete if the request method is "
                                           "POST.And if the request method is GET it returns a list of all "
                                           "athletes.Can be accessed by ADMINS or COACHES.",
                     responses={200: SportSerializer})
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def sports(request):
    sport = Sports.objects.all()
    sport_serializer = SportSerializer(sport, many=True)
    return JsonResponse(sport_serializer.data, safe=False, status=HTTP_200_OK)
