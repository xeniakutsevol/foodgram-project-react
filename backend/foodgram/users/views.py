from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscription
from .serializers import SubscriptionSerializer

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    @action(
        methods=["post", "delete"],
        detail=True,
        url_path="subscribe",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe_unsubscribe(self, request, id=None):
        user = self.request.user
        subscription = get_object_or_404(User, id=id)
        obj_exists = Subscription.objects.filter(
            subscription=subscription, user=user
        ).exists()
        if request.method == "POST":
            if user == subscription:
                return Response(
                    {"errors": "Нельзя подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not obj_exists:
                subscriptions = Subscription.objects.create(
                    subscription=subscription, user=user
                )
                serializer = SubscriptionSerializer(subscriptions)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(
                {"errors": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif request.method == "DELETE":
            if not obj_exists:
                return Response(
                    {"errors": "Вы еще не подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                Subscription.objects.filter(
                    subscription=subscription, user=user
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["get"],
        detail=False,
        url_path="subscriptions",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_subscriptions(self, request):
        user = self.request.user
        queryset = Subscription.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(data=page, many=True)
        serializer.is_valid(raise_exception=True)
        return self.get_paginated_response(serializer.data)
