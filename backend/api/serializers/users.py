from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe
from users.models import User


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткая сводка рецепта."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class UserSerializer(serializers.ModelSerializer):
    """Пользователь/список пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return request.user.follower.filter(author=obj).exists()


class UserRegSerializer(UserCreateSerializer):
    """Создание пользователя."""
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return request.user.follower.filter(author=obj).exists()

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
