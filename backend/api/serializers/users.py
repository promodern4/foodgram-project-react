from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework import serializers
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


class PasswordSerializer(serializers.Serializer):
    """Смена пароля."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, new_password):
        validate_password(new_password)
        return new_password


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
