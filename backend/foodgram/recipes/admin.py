from django.contrib import admin

from .models import (Favorited, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)

admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorited)
admin.site.register(ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name', 'tags')
    list_display = ('id', 'author', 'name')
    readonly_fields = ('favorites_count',)
    fields = ('tags', 'image', 'name', 'text', 'cooking_time',
              'favorites_count',)

    def favorites_count(self, obj):
        print(obj.favorited.count)
        return obj.favorited.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )
    list_display = ('name', 'measurement_unit')
