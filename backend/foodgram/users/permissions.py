from rest_framework import permissions


class UsersPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return not (view.action == 'me' and request.user.is_anonymous)
