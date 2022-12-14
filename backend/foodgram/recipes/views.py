import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (Favorited, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import (FavoritedPermission, IsAuthorPermission,
                          ShoppingCartPermission)
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name", "name")


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("author",)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        is_favorited = self.request.query_params.get("is_favorited", None)
        is_in_shopping_cart = self.request.query_params.get("is_in_shopping_cart", None)
        tags_ids = self.request.query_params.getlist("tags", None)
        if is_favorited is not None:
            queryset = queryset.filter(favorited__user=user)
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(shopping_cart__user=user)
        if tags_ids:
            queryset = queryset.filter(tags__slug__in=tags_ids).distinct()
        if self.action == "get_shopping_cart":
            recipes_in_sc_ids = ShoppingCart.objects.filter(
                user=user).values_list("recipe", flat=True)
            queryset = queryset.filter(id__in=recipes_in_sc_ids)
        if self.action == "download_shopping_cart":
            recipes_in_sc_ids = ShoppingCart.objects.filter(
                user=user).values_list("recipe", flat=True)
            queryset = (
                IngredientInRecipe.objects.filter(recipe__in=recipes_in_sc_ids)
                .values("ingredient__name", "ingredient__measurement_unit")
                .annotate(amount_sum=Sum("amount"))
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeReadSerializer
        if self.action == "retrieve":
            return RecipeReadSerializer
        elif self.action in (
            "add_remove_shopping_cart",
            "get_shopping_cart",
            "add_remove_favorite",
        ):
            return RecipeShortSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        if (self.action == "download_shopping_cart" and self.request.method == "GET"):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.request.method == "GET":
            self.permission_classes = (permissions.AllowAny,)
        elif (self.action == "add_remove_shopping_cart" and self.request.method == "DELETE"):
            self.permission_classes = (ShoppingCartPermission,)
        elif (self.action == "add_remove_favorite" and self.request.method == "DELETE"):
            self.permission_classes = (FavoritedPermission,)
        elif self.request.method in ("PATCH", "DELETE"):
            self.permission_classes = (IsAuthorPermission,)
        else:
            self.permission_classes = (permissions.IsAuthenticated,)
        return super(RecipeViewSet, self).get_permissions()

    @action(methods=["post", "delete"], detail=True, url_path="shopping_cart")
    def add_remove_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        obj_exists = ShoppingCart.objects.filter(
            recipe=recipe, user=user).exists()
        serializer = self.get_serializer(recipe)
        if request.method == "POST":
            if not obj_exists:
                ShoppingCart.objects.create(recipe=recipe, user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"errors": "???????????? ?????? ?? ???????????? ??????????????."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif request.method == "DELETE":
            if not obj_exists:
                return Response(
                    {"errors": "???????????? ???? ?????? ?? ???????????? ??????????????."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                ShoppingCart.objects.filter(recipe=recipe, user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=False, url_path="shopping_cart")
    def get_shopping_cart(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        queryset = self.get_queryset()
        output = []
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="to_buy.csv"'
        writer = csv.writer(response)
        writer.writerow(["???????????????? ??????????????????????", "?????????????? ??????????????????", "?????????????????? ????????????????????"])
        for obj in queryset:
            output.append(
                [
                    obj.get("ingredient__name"),
                    obj.get("ingredient__measurement_unit"),
                    obj.get("amount_sum"),
                ]
            )
        writer.writerows(output)
        return response

    @action(methods=['post', 'delete'], detail=True, url_path='favorite')
    def add_remove_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        obj_exists = Favorited.objects.filter(
            recipe=recipe, user=user).exists()
        serializer = self.get_serializer(recipe)
        if request.method == 'POST':
            if not obj_exists:
                Favorited.objects.create(recipe=recipe, user=user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': '???????????? ?????? ?? ??????????????????.'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if not obj_exists:
                return Response({'errors': '???????????? ???? ?????? ?? ??????????????????.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                Favorited.objects.filter(recipe=recipe, user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
