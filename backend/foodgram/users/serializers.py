from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    pass
