from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Cart, Favourite, Follow, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOwnerOrReadOnly
from .serializers.recipes import (IngredientSerializer, RecipeCreateSerializer,
                                  RecipeSerializer, ShortRecipeReadSerializer,
                                  TagSerializer)
from .serializers.users import SubscriptionsSerializer, UserSerializer


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date',)
    ordering = ('pub_date',)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            new_queryset = Recipe.objects.all().annotate(
                is_favorited=Exists(Favourite.objects.filter(
                    user=user,
                    recipe=OuterRef("pk")
                )),
                is_in_shopping_cart=Exists(Cart.objects.filter(
                    user=user,
                    recipe=OuterRef("pk")
                ))
            )
        else:
            new_queryset = Recipe.objects.all()
        return new_queryset

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        if request.method == 'POST':
            if user.favorite.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен в список избранного!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite_recipe = Favourite.objects.create(
                user=user, recipe=recipe
            )
            serializer = ShortRecipeReadSerializer(
                recipe
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not user.favorite.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепта нет в списке избранного!"}
                )
            favorite_recipe = get_object_or_404(
                Favourite,
                user=user,
                recipe=recipe
            )
            favorite_recipe.delete()
            return Response(
                {"details": "Рецепт удален из издранных!"},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        if request.method == 'POST':
            if user.cart.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен в список покупок!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_recipe = Cart.objects.create(
                user=user, recipe=recipe
            )
            serializer = ShortRecipeReadSerializer(
                recipe
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not user.cart.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепта нет в списке покупок!"}
                )
            cart_recipe = get_object_or_404(
                Cart,
                user=user,
                recipe=recipe
            )
            cart_recipe.delete()
            return Response(
                {"details": "Рецепт успешно удален из списка покупок!"},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart__user=request.user
            ).values('ingredient').annotate(
                amount=Sum('amount')
            ).values_list(
                'ingredient__name',
                'ingredient__measurement_unit',
                'amount'
            )
        )
        shopping_cart = 'Список продуктов:\n'
        for item in ingredients:
            shopping_cart += (
                f'{item[0]} ({item[1]}) - {item[2]}\n'
            )
        response = HttpResponse(shopping_cart, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt'
        )
        return response


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=('get',),
    )
    def me(self, request):
        self.get_object = self.get_instance
        return self.retrieve(request)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        follows = request.user.follower.all().values_list('author', flat=True)
        authors = User.objects.filter(id__in=list(follows))
        results = self.paginate_queryset(authors)
        serializer = SubscriptionsSerializer(
            results,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(
            User,
            id=id
        )
        if self.request.method == 'POST':
            if user.follower.filter(author=author).exists():
                return Response(
                    {"errors": "Вы уже подписаны!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {"errors": "Вы пытаетесь подписаться на самого себя!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.create(
                user=user,
                author=author
            )
            author = User.objects.get(id=follow.author.id)
            serializer = SubscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if self.request.method == 'DELETE':
            if user.follower.filter(author=author).exists():
                follow = get_object_or_404(
                    Follow,
                    user=request.user,
                    author=author
                )
                follow.delete()
                return Response(
                    {"details": "Подписка удалена"},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {"errors": "Вы не подписаны на этого автора!"},
                status=status.HTTP_400_BAD_REQUEST
            )
