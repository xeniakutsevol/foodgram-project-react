from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from recipes.models import Recipe
from rest_framework import serializers

from .models import Subscription

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed")

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Subscription.objects.filter(
                user=user, subscription=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="subscription.email")
    id = serializers.ReadOnlyField(source="subscription.id")
    username = serializers.ReadOnlyField(source="subscription.username")
    first_name = serializers.ReadOnlyField(source="subscription.first_name")
    last_name = serializers.ReadOnlyField(source="subscription.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source="subscription.recipes.count")

    class Meta:
        model = Subscription
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, subscription=obj.subscription
        ).exists()

    def get_recipes(self, obj):
        # импорт здесь, чтобы избежать circular import error
        from recipes.serializers import RecipeShortSerializer

        queryset = Recipe.objects.filter(author=obj.subscription)
        return RecipeShortSerializer(queryset, many=True).data
