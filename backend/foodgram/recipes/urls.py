from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path("", include(router.urls)),
]