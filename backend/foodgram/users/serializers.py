from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import Subscription
from recipes.models import Recipe

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, subscription=obj).exists()
        return False

class SubscriptionSerializer(BaseUserSerializer):
    # импорт здесь, чтобы избежать circular import error
    from recipes.serializers import RecipeShortSerializer
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')
    
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, subscription=obj).exists()
        return False
    
    def get_recipes_count(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Recipe.objects.filter(author=obj).count()