from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='is_favorited_method'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_method'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_method(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            queryset = queryset.filter(favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            queryset = queryset.filter(cart__user=self.request.user)
        return queryset
