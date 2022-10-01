from django.shortcuts import get_object_or_404
from rest_framework import serializers
from users.serializers import UserSerializer

from .fields import Base64ImageField
from .models import (Favorited, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source="inginrecipe", many=True, read_only=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Favorited.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
    ingredients = IngredientInRecipeSerializer(source="inginrecipe", many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Favorited.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False

    def add_nested_data(self, ingredients, recipe):
        inginrecipe_objs = []
        for ing in ingredients:
            inginrecipe_objs.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=get_object_or_404(Ingredient, pk=ing["id"]),
                    amount=ing["amount"],
                )
            )
        IngredientInRecipe.objects.bulk_create(inginrecipe_objs)

    def create(self, validated_data):
        ingredients = self.context["request"].data["ingredients"]
        validated_data.pop("inginrecipe")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.add_nested_data(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.context["request"].data["ingredients"]
        validated_data.pop("inginrecipe")
        tags = validated_data.pop("tags")
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.save()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.add_nested_data(ingredients, instance)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
