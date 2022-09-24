from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, Q

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = ColorField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=200)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='recipes')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes',
        through='recipes.IngredientInRecipe')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            CheckConstraint(
                check=Q(cooking_time__gte=1),
                name='check_cooking_time',
            ),
        ]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='inginrecipe')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='inginrecipe')
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return (f"{self.recipe.name}: {self.ingredient} "
                f"{self.ingredient.measurement_unit}, {self.amount}")


class Favorited(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorited')

    def __str__(self):
        return self.recipe.name


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')

    def __str__(self):
        return self.recipe.name
