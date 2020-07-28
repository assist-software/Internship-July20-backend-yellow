from math import ceil

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Club.serializers import ClubSerializer, MembersClubSerializer, MemberSerializer
from Events.models import Events
from Events.serializers import EventsSerializer
from users.models import User
from rest_framework.decorators import permission_classes, api_view
from Club.models import Club, MembersClub
from rest_framework.permissions import IsAuthenticated
from api.permissions import AthletePermission, AllPermission, AdminORCoachPermission

""" Requests for 'api/club/' path. """

param1 = openapi.Parameter('name', openapi.IN_QUERY, description="name", type=openapi.TYPE_STRING)
param2 = openapi.Parameter('coach name', openapi.IN_QUERY, description="coach name", type=openapi.TYPE_STRING)


@swagger_auto_schema(method='get',
                     operation_description="Getting the list of clubs: The ADMIN will see all the clubs.The COACH "
                                           "just the one that he/she owns.The ATHLETE will see the ones that he/she "
                                           "is invited/ requested to enter/ is a member",
                     responses={200: ClubSerializer,
                                400: "Bad request"})
@swagger_auto_schema(methods=['post'],
                     operation_description="Creating new club: Just the COACH have access",
                     manual_parameters=[param1, param2],
                     responses={200: ClubSerializer})
@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes((IsAuthenticated, AllPermission,))
def create_club(request):
    """
    Creating new club:
    Just the COACH have access
    :param request:
    :return: ClubSerializer:
    """

    if request.method == "POST":
        if request.user.role == User.ATHLETE:
            return Response({'error': 'Access denied.'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role == User.COACH:
            name = request.data.get('name')
            if name is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                test = Club.objects.get(name=name)
                return Response({"error": "Club already exists!"}, status=status.HTTP_400_BAD_REQUEST)
            except Club.DoesNotExist:
                club = Club(name=name, id_Owner=request.user)
        else:
            coach_name = request.data.get('coach')
            if coach_name is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            coach_name = coach_name.split()
            coach = User.objects.get(first_name=coach_name[0], last_name=coach_name[1])
            club = Club(name=request.data.get('name'), id_Owner=coach)
        club.save()
        users = User.objects.all()
        for us in users:
            non_member = MembersClub(id_User=us, id_club=club, is_invited=False, is_requested=False, is_member=False)
            non_member.save()
        serializers = ClubSerializer(data=club.__dict__)
        """
        if serializers.is_valid():
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        """
        return Response(status=status.HTTP_201_CREATED)

    """ Getting the list of clubs: 
    The ADMIN will see all the clubs.
    The COACH just the one that he/she owns.
    The ATHLETE will see the ones that he/she is invited/ requested to enter/ is a member"""

    if request.method == "GET":
        search = request.query_params.get('search')
        if search is None:
            search = ""
        if request.user.role == User.ATHLETE:
            clubs = MembersClub.objects.filter(id_User=request.user)
            club_serializer = MembersClubSerializer(clubs, many=True)
            return JsonResponse(club_serializer.data, safe=False)
        elif request.user.role == User.COACH:
            clubs = Club.objects.filter(id_Owner=request.user)
            final = list()
            member_numbers = list()
            for club in clubs:
                number = len(MembersClub.objects.filter(id_club=club.id, is_member=True))
                member_numbers.append({club.id: number})
                if search.lower() in club.name.lower():
                    final.append(club)
            club_serializer = ClubSerializer(final, many=True)
            return JsonResponse({"clubs": club_serializer.data,
                                 "numbers": member_numbers}, safe=False)
        clubs = Club.objects.all()
        final = list()
        member_numbers = list()
        for club in clubs:
            number = len(MembersClub.objects.filter(id_club=club.id, is_member=True))
            member_numbers.append({club.id: number})
            if search.lower() in club.name.lower():
                final.append(club)
        club_serializer = ClubSerializer(final, many=True)
        return JsonResponse({"clubs": club_serializer.data,
                                 "numbers": member_numbers}, safe=False)


""" Requests for 'api/club/<int:club_id>' path. """


@swagger_auto_schema(methods=['put'],
                     operation_description="Edit a club by ID:Just the ADMIN has access to edit a club.",
                     manual_parameters=[param1],
                     responses={200: ClubSerializer})
@swagger_auto_schema(methods=['delete'],
                     operation_description="Deleting a club: The ADMIN will be able to delete a club.",
                     responses={200: 'success : The club has been deleted.',
                                404: "Bad request"})
@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
@permission_classes((IsAuthenticated, AllPermission))
def show_club(request, club_id):
    """
    Getting a club by ID:
    The ADMIN will be able to see all the clubs, no matter the ID and owner.
    The COACH will be able to see all the clubs he/she owns, no matter the ID.
    :param request:
    :param club_id:
    :return: MembersClubSerializer:
    """

    if request.method == "GET":
        if request.user.role == User.ATHLETE:
            club = get_object_or_404(Club, id=club_id)
            coach_clubs = Club.objects.filter(id_Owner=club.id_Owner)
            coach_clubs_serializer = ClubSerializer(coach_clubs, many=True)
            club_serializer = ClubSerializer(club)
            members = MembersClub.objects.filter(id_club=club_id)
            members_serializer = MembersClubSerializer(members, many=True)
            events = Events.objects.filter(club_id=club_id)
            events_serializer = EventsSerializer(events, many=True)
            return JsonResponse({'Club details': club_serializer.data, 'Members': members_serializer.data,
                                 'Events': events_serializer.data, 'Coach clubs': coach_clubs_serializer.data},
                                status=status.HTTP_200_OK)
        elif request.user.role == User.COACH or request.user.role == User.ADMIN:  # merge
            search = request.query_params.get('search')
            if search is None:
                search = ""
            page = request.query_params.get('page')
            on_page = 9
            if page is not None:
                page = int(page)
                if page == 1:
                    start = 0
                else:
                    start = ((page - 1) * (on_page - 1)) + 1
            club = get_object_or_404(Club, id=club_id)
            club_serializer = ClubSerializer(club)
            members = MembersClub.objects.filter(id_club=club_id, is_member=True)
            final = list()
            for memb in members:
                if search.lower() in memb.id_User.get_full_name().lower():
                    final.append(memb)
            members_serializer = MemberSerializer(final, many=True)
            if club.id_Owner == request.user or request.user.role == User.ADMIN:
                return JsonResponse({'Club_details': club_serializer.data,
                                     'Members': members_serializer.data[start:start+on_page],
                                     "page_number": ceil(len(members_serializer.data)/on_page),})
            else:
                return JsonResponse({'error': 'Access denied.'}, status=status.HTTP_401_UNAUTHORIZED)
        question = (get_object_or_404(Club, id=club_id))
        return Response({"name": question.name})

    """ Edit a club by ID:
    Just the ADMIN has access to edit a club."""

    if request.method == "PUT":
        if request.user.role == User.ATHLETE or request.user.role == User.COACH:
            return Response({'error': 'Access denied.'})

        question = (get_object_or_404(Club, id=club_id))
        question.name = request.data.get('name')
        question.save()
        return Response({"name": question.name})

    """ Deleting a club:
    Just the ADMIN has access to delete a club."""

    if request.method == "DELETE":
        if request.user.role == User.ATHLETE or request.user.role == User.COACH:
            return Response({'error': 'Access denied.'})

        question = (get_object_or_404(Club, id=club_id))
        question.delete()
        return Response({"Club has been deleted!"}, status=status.HTTP_410_GONE)


""" Requests for 'api/club/<int:club_id>/join/' path. """


@swagger_auto_schema(methods=['post'],
                     operation_description="Joining a club by ID:Just the ATHLETE has access to access the join path "
                                           "and he will be registered in a list of members the requested to enter the"
                                           " club.",
                     responses={200: 'Success : Your request had been registered',
                                302: "Your requested already to join this club"})
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated, AthletePermission,))
def join_club(request, club_id):
    """ Joining a club by ID:
    Just the ATHLETE has access to access the join path and he will be registered
    in a list of members the requested to enter the club."""

    if request.user.role == User.COACH or request.user.role == User.ADMIN:
        return Response({'error': 'Access denied.'})
    if MembersClub.objects.filter(id_User=request.user, id_club=get_object_or_404(Club, id=club_id), is_requested=True):
        return Response({"Your requested already to join this club"})
    else:
        new_member = (get_object_or_404(MembersClub, id_club=club_id, id_User=request.user))
        new_member.is_requested = True
        new_member.save()
        return Response({"Your request had been registered"}, status=status.HTTP_202_ACCEPTED)


""" Requests for 'api/club/<int:club_id>/requested' path. """


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated, AllPermission,))
def mb_requested_club(request, club_id):
    """ Getting a club by ID:
    The ADMIN will be able to see all the clubs, no matter the ID and owner.
    The COACH will be able to see all the clubs he/she owns, no matter the ID
    (but he/she will see the ATHLETES that REQUESTED to join the club)."""
    if request.method == "GET":
        search = request.query_params.get('search')
        if search is None:
            search = ""
        page = request.query_params.get('page')
        on_page = 9
        if page is not None:
            page = int(page)
            if page == 1:
                start = 0
            else:
                start = ((page - 1) * (on_page - 1)) + 1
        club = get_object_or_404(Club, id=club_id)
        club_serializer = ClubSerializer(club)
        members = MembersClub.objects.filter(id_club=club_id, is_requested=True)
        final = list()
        for memb in members:
            if search.lower() in memb.id_User.get_full_name().lower():
                final.append(memb)
        members_serializer = MemberSerializer(final, many=True)
        if club.id_Owner == request.user or request.user.role == User.ADMIN:
            return JsonResponse({'Club_details': club_serializer.data,
                                 'Members': members_serializer.data[start:start + on_page],
                                 "page_number": ceil(len(members_serializer.data) / on_page)})
        else:
            return JsonResponse({'error': 'Access denied.'}, status=status.HTTP_401_UNAUTHORIZED)
    question = (get_object_or_404(Club, id=club_id))
    return Response({"name": question.name})



@swagger_auto_schema(methods=['get'],
                     operation_description="Getting a list of clubs",
                     responses={200: ClubSerializer})
@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def clubs(request):
    if request.user.role == User.ADMIN:
        clubs = Club.objects.all().values("id", "name")
    else:
        clubs = Club.objects.filter(id_Owner=request.user).values("id", "name")
    return Response(clubs, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def accept_request(request):
    user_id = request.data.get('user_id')
    if id is None:
        return Response({"error": "Provide an user_id"}, status=status.HTTP_400_BAD_REQUEST)
    club_id = request.data.get('club_id')
    if club_id is None:
        return Response({"error": "Provide an id"}, status=status.HTTP_400_BAD_REQUEST)
    accept = int(request.data.get(''))
    if accept is None:
        return Response({"error": "Provide an decision."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        members = MembersClub.objects.get(id_club=club_id, id_User=user_id)
        if accept == True:
            members.is_member = 1
        members.is_requested = 0
        members.save()
    except MembersClub.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)