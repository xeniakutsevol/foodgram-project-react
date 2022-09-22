from rest_framework import permissions
from .models import ShoppingCart


class IsAuthorPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ShoppingCartPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return ShoppingCart.objects.get(recipe=obj.id).user == request.user