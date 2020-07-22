from rest_framework import permissions
from rest_framework.authtoken.models import Token
from users.models import User


class AdminPermission(permissions.BasePermission):
    # Permission for ADMIN users
    def has_permission(self, request, view):
        header = request.META['HTTP_AUTHORIZATION']
        if header is None:
            return False
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return False
        user = User.objects.get(id=token.user_id)
        if user.role != User.ADMIN:
            return False
        return True


class CoachPermission(permissions.BasePermission):
    # Permission for COACH users
    def has_permission(self, request, view):
        header = request.META['HTTP_AUTHORIZATION']
        import ipdb
        ipdb.set_trace()
        if header is None:
            return False
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return False
        user = User.objects.get(id=token.user_id)
        if user.role != User.COACH:
            return False
        return True


class AdminANDCoachPermission(permissions.BasePermission):
    # Permission for ADMIN or COACH users
    def has_permission(self, request, view):
        header = request.META['HTTP_AUTHORIZATION']
        if header is None:
            return False
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return False
        user = User.objects.get(id=token.user_id)
        if user.role != User.ADMIN and user.role != User.COACH:
            return False
        return True


class AthletePermission(permissions.BasePermission):
    # Permission for COACH users
    def has_permission(self, request, view):
        header = request.META['HTTP_AUTHORIZATION']
        if header is None:
            return False
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return False
        user = User.objects.get(id=token.user_id)
        if user.role != User.ATHLETE:
            return False
        return True


class AllPermission(permissions.BasePermission):
    # Permission for COACH users
    def has_permission(self, request, view):
        header = request.META['HTTP_AUTHORIZATION']
        if header is None:
            return False
        try:
            token = Token.objects.get(key=header)
        except Token.DoesNotExist:
            return False