from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Subscription
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import SubscriptionSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    @action(methods=['post', 'delete'], detail=True, url_path='subscribe', permission_classes=(permissions.IsAuthenticated,))
    def subscribe_unsubscribe(self, request, id=None):
        user = self.request.user
        subscription = get_object_or_404(User, id=id)
        obj_exists = Subscription.objects.filter(subscription=subscription, user=user).exists()
        if request.method == 'POST':
            if user == subscription:
                return Response({'errors': 'Нельзя подписаться на себя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not obj_exists:
                subscriptions = Subscription.objects.create(subscription=subscription, user=user)
                serializer = SubscriptionSerializer(subscriptions)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': 'Вы уже подписаны на этого пользователя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if not obj_exists:
                return Response({'errors': 'Вы еще не подписаны на этого пользователя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                Subscription.objects.filter(subscription=subscription, user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)