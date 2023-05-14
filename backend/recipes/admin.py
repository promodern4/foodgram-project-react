from django.contrib import admin

from .models import (Cart,
                     Favourite,
                     Ingredient,
                     Recipe,
                     RecipeIngredient,
                     Tag)


class ItemInline(admin.StackedInline):
    model = RecipeIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit'
    )
    search_fields = (
        'name', 'measurement_unit'
    )
    list_filter = (
        'name',
    )
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [ItemInline]
    list_display = (
        'id', 'author', 'name', 'text',
        'cooking_time'
    )
    search_fields = (
        'name', 'author', 'tags'
    )
    list_filter = (
        'author', 'name', 'tags'
    )
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug'
    )
    search_fields = (
        'name', 'slug'
    )
    empty_value_display = '-empty-'


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
