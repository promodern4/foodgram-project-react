from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

# Пользователи


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


# Тэги и ингредиенты

class TagSerializer(serializers.ModelSerializer):
    """Тэги."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


# Рецепты

class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткая сводка рецепта."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Полная сводка ингредиента."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReciperCreateIngredientSerializer(serializers.ModelSerializer):
    """Добавление ингредиента."""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Полная сводка рецепта."""
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe')
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time', 'pub_date',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return request.user.cart.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание/обновление рецепта."""
    ingredients = ReciperCreateIngredientSerializer(
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        extra_kwargs = {
            'ingredients': {'required': True},
            'tags': {'required': True},
            'image': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True}
        }

    def validate(self, obj):
        ingredients_list = [ingredient['id'] for ingredient in obj.get(
            'ingredients')]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )
        return obj

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient['id']
                ),
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(
            recipe__id=instance.id
        ).delete()
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=instance,
                ingredient=Ingredient.objects.get(
                    id=ingredient['id']
                ),
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.save()
        return instance
