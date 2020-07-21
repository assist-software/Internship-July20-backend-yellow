from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Club.serializers import ClubSerializer
from users.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes, api_view
from Club.models import Club, MembersClub

""" Requests for 'api/club/' path. """


@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes((AllowAny,))
def create_club(request):
    """ Creating new club:
    Just the COACH have access"""
    if request.method == "POST":

        header = request.headers.get('Authorization')
        if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=token.user_id)
        if user.role == 2 or user.role == 0:
            return Response({'error': 'Access denied.'})

        club = Club(name=request.data.get('name'), id_Owner=user)
        club.save()
        serializers = ClubSerializer(data=club.__dict__)
        if serializers.is_valid():
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    """ Getting the list of clubs: 
    The ADMIN will see all the clubs.
    The COACH just the one that he/she owns."""
    if request.method == "GET":

        header = request.headers.get('Authorization')
        if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=token.user_id)
        if user.role == 2:
            return Response({'error': 'Access denied.'})
        elif user.role == 1:
            clubs = Club.objects.filter(id_Owner=user)
            club_serializer = ClubSerializer(clubs, many=True)
            return JsonResponse(club_serializer.data, safe=False)
        clubs = Club.objects.all()
        club_serializer = ClubSerializer(clubs, many=True)
        return JsonResponse(club_serializer.data, safe=False)


""" Requests for 'api/club/<int:club_id>' path. """


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
@permission_classes((AllowAny,))
def show_club(request, club_id):
    """ Getting a club by ID:
    The ADMIN will be able to see all the clubs, no matter the ID and owner.
    The COACH will be able to see all the clubs he/she owns, no matter the ID."""
    if request.method == "GET":

        header = request.headers.get('Authorization')
        if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=token.user_id)
        if user.role == 2:
            return Response({'error': 'Access denied.'})
        elif user.role == 1:  # merge
            question = (get_object_or_404(Club, id=club_id))
            if question.id_Owner == user:
                club_serializer = ClubSerializer(question)
                return JsonResponse(club_serializer.data, safe=False)
            else:
                return JsonResponse({'error': 'Access denied.'}, status=status.HTTP_401_UNAUTHORIZED)
        question = (get_object_or_404(Club, id=club_id))
        return Response({"name": question.name})
    """ Edit a club by ID:
    Just the ADMIN has access to edit a club."""
    if request.method == "PUT":

        header = request.headers.get('Authorization')
        if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=token.user_id)
        if user.role == 2 or user.role == 1:
            return Response({'error': 'Access denied.'})

        question = (get_object_or_404(Club, id=club_id))
        question.name = request.data.get('name')
        question.save()
        return Response({"name": question.name})
    """ Deleting a club:
    Just the ADMIN has access to delete a club."""
    if request.method == "DELETE":

        header = request.headers.get('Authorization')
        if header is None:
            return Response({'error': 'Access denied. (Header Token)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=token.user_id)
        if user.role == 2 or user.role == 1:
            return Response({'error': 'Access denied.'})

        question = (get_object_or_404(Club, id=club_id))
        question.delete()
        return Response({"Club has been deleted!"}, status=status.HTTP_410_GONE)


""" Requests for 'api/club/<int:club_id>/join/' path. """


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def join_club(request, club_id):
    """ Joining a club by ID:
    Just the ATHLETE has access to access the join path and he will be registered
    in a list of members the requested to enter the club."""
    header = request.headers.get('Authorization')
    if header is None:
        return Response({'error': 'Access denied. (Header Token)'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key=header)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid Token'},
                        status=status.HTTP_404_NOT_FOUND)
    user = User.objects.get(id=token.user_id)
    if user.role == 1 or user.role == 0:
        return Response({'error': 'Access denied.'})
    if MembersClub.objects.filter(id_User=user, id_club=get_object_or_404(Club, id=club_id)):
        return Response({"Your requested already to join this club"})
    else:
        new_member = MembersClub(id_User=user, id_club=get_object_or_404(Club, id=club_id), is_requested=True)
        new_member.save()
        serializers = ClubSerializer(data=club.__dict__)
        if serializers.is_valid():
            return Response({"Your request had been registered"}, status=status.HTTP_202_ACCEPTED)