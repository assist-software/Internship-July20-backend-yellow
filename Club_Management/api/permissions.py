from rest_framework import permissions
from rest_framework.authtoken.models import Token
from users.models import User


class AdminPermission(permissions.BasePermission):
    # Permission for ADMIN users
    def has_permission(self, request, view):
        return request.user.role == User.ADMIN


class CoachPermission(permissions.BasePermission):
    # Permission for COACH users
    def has_permission(self, request, view):
        return request.user.role == User.COACH


class AdminORCoachPermission(permissions.BasePermission):
    # Permission for ADMIN or COACH users
    def has_permission(self, request, view):
        return request.user.role == User.ADMIN or request.user.role == User.COACH


class AthletePermission(permissions.BasePermission):
    # Permission for COACH users
    def has_permission(self, request, view):
        return request.user.role == User.ATHLETE


class AllPermission(permissions.BasePermission):
    # Permission for All users
    def has_permission(self, request, view):
        return request.user.role == User.ADMIN or request.user.role == User.COACH or request.user.role == User.ATHLETE
