from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Club.serializers import ClubSerializer, MembersClubSerializer
from Events.models import Events
from Events.serializers import EventsSerializer
from users.models import User
from rest_framework.decorators import permission_classes, api_view
from Club.models import Club, MembersClub
from rest_framework.permissions import IsAuthenticated
from api.permissions import AthletePermission, AllPermission, AdminORCoachPermission

""" Requests for 'api/club/' path. """


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
            club = Club(name=request.data.get('name'), id_Owner=request.user)
        else:
            name = request.data.get('coach')
            name = name.split()
            coach = User.objects.get(first_name=name[0], last_name=name[1])
            club = Club(name=request.data.get('name'), id_Owner=coach)
        club.save()
        users = User.objects.all()
        for us in users:
            non_member = MembersClub(id_User=us, id_club=club, is_invited=False, is_requested=False, is_member=False)
            non_member.save()
        serializers = ClubSerializer(data=club.__dict__)
        if serializers.is_valid():
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


    """ Getting the list of clubs: 
    The ADMIN will see all the clubs.
    The COACH just the one that he/she owns.
    The ATHLETE will see the ones that he/she is invited/ requested to enter/ is a member"""

    if request.method == "GET":
        if request.user.role == User.ATHLETE:
            clubs = MembersClub.objects.filter(id_User=request.user)
            club_serializer = MembersClubSerializer(clubs, many=True)
            return JsonResponse(club_serializer.data, safe=False)
        elif request.user.role == User.COACH:
            clubs = Club.objects.filter(id_Owner=request.user)
            club_serializer = ClubSerializer(clubs, many=True)
            return JsonResponse(club_serializer.data, safe=False)
        clubs = Club.objects.all()
        club_serializer = ClubSerializer(clubs, many=True)
        return JsonResponse(club_serializer.data, safe=False)


""" Requests for 'api/club/<int:club_id>' path. """


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



        elif request.user.role == User.COACH:  # merge
            clubs = MembersClub.objects.filter(id_club=club_id, is_member=True)
            club = (get_object_or_404(Club, id=club_id))
            if club.id_Owner == request.user:
                club_serializer = MembersClubSerializer(clubs, many=True)
                return JsonResponse(club_serializer.data, safe=False)
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


@csrf_exempt
@api_view(["POST"])
@permission_classes((AthletePermission,))
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
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def mb_requested_club(request, club_id):
    """ Getting a club by ID:
    The ADMIN will be able to see all the clubs, no matter the ID and owner.
    The COACH will be able to see all the clubs he/she owns, no matter the ID
    (but he/she will see the ATHLETES that REQUESTED to join the club)."""
    if request.method == "GET":
        if request.user.role == User.ATHLETE:
            return Response({'error': 'Access denied.'})
        elif request.user.role == User.COACH:  # merge
            clubs = MembersClub.objects.filter(id_club=club_id, is_requested=True)
            club = (get_object_or_404(Club, id=club_id))
            if club.id_Owner == request.user:
                club_serializer = MembersClubSerializer(clubs, many=True)
                return JsonResponse(club_serializer.data, safe=False)
            else:
                return JsonResponse({'error': 'Access denied.'}, status=status.HTTP_401_UNAUTHORIZED)
        clubs = (get_object_or_404(Club, id=club_id))
        return Response({"name": clubs.name})


""" Requests for 'api/club/<int:club_id>/pending' path. """


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def mb_pending_club(request, club_id):
    """ Getting a club by ID:
    The ADMIN will be able to see all the clubs, no matter the ID and owner.
    The COACH will be able to see all the clubs he/she owns, no matter the ID
    (but he/she will see the ATHLETES that are PENDING on the invitation to join the club)."""
    if request.method == "GET":
        if request.user.role == User.ATHLETE:
            return Response({'error': 'Access denied.'})
        elif request.user.role == User.COACH:  # merge
            clubs = MembersClub.objects.filter(id_club=club_id, is_invited=True)
            club = (get_object_or_404(Club, id=club_id))
            if club.id_Owner == request.user:
                club_serializer = MembersClubSerializer(clubs, many=True)
                return JsonResponse(club_serializer.data, safe=False)
            else:
                return JsonResponse({'error': 'Access denied.'}, status=status.HTTP_401_UNAUTHORIZED)
        clubs = (get_object_or_404(Club, id=club_id))
        return Response({"name": clubs.name})


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated, AdminORCoachPermission,))
def clubs(request):
    if request.user.role == User.ADMIN:
        clubs = Club.objects.all().values("name")
    else:
        clubs = Club.objects.filter(id_Owner=request.user).values("name")
    final_list = list()
    for club in clubs:
        final_list.append(club["name"])
    return Response(final_list, status=status.HTTP_200_OK)