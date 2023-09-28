from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .validators import (
    ColorFieldValidator,
    CookingTimeRecipeFieldValidator,
    RecipeIngredientFieldValidator,
    UsernameFieldValidator,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    """Сериалайзер для создания нового пользователя."""

    username = UsernameFieldValidator()

    class Meta(BaseUserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserListSerializer(BaseUserSerializer):
    """Сериализатор для подписанных пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def to_representation(self, instance):
        user = self.context.get('request').user

        if user.is_authenticated:
            return super().to_representation(instance)
        data = super().to_representation(instance)
        data['email'], data['username'] = None, None
        return data

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            user.is_anonymous and author.subscribed.filter(user=user).exists()
        )


class UserSetPasswordSerializer(serializers.Serializer):
    """Сериализатор для создания пароля."""

    new_password = serializers.CharField(required=True, write_only=True)
    current_password = serializers.CharField(required=True, write_only=True)


class RecipeListShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецептах."""

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для перечисления подписок пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            user.is_anonymous and author.subscribed.filter(user=user).exists()
        )

    def get_recipes(self, author):
        request = self.context.get('request')
        user = self.context.get('request').user
        if user.is_anonymous:
            return None

        recipes = author.recipes.filter(author=author)
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        else:
            recipes = recipes.all()
        return RecipeListShortSerializer(
            instance=recipes, many=True, context={'request': request}
        ).data


class SubscribeSerializer(serializers.Serializer):
    """Сериализатор для оформления подписки на пользователя."""

    def validate(self, data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=self.context.get('id'))
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя самого'
            )
        if author.subscribed.filter(user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=validated_data.get('id'))
        author.subscribed.create(user=user)
        return SubscriptionSerializer(
            instance=author, context={'request': self.context.get('request')}
        ).data


class TagSerializer(serializers.ModelSerializer):
    color = ColorFieldValidator()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели тегов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингридиентов."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientAddSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели ингредиентов рецепта."""

    id = serializers.IntegerField(source='ingredient.id')
    amount = RecipeIngredientFieldValidator()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserListSerializer(
        default=serializers.CurrentUserDefault(), read_only=True
    )
    ingredients = RecipeIngredientSerializer(
        many=True, source='ingredient_amount', read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        return recipe.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return user.is_anonymous and recipe.shoppingcart(user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка рецептов."""

    ingredients = RecipeIngredientAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=True)
    cooking_time = CookingTimeRecipeFieldValidator()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients_data):
        unique_ingredients = set()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').get('id')
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты не должны дублироваться'}
                )
            unique_ingredients.add(ingredient_id)
        return ingredients_data

    def set_ingredients(self, recipe, ingredients_data):
        ingredients = list()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').get('id')
            amount = ingredient_data.get('amount')
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)

            recipe_ingredient = RecipeIngredient(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
            ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance=instance, context={'request': self.context.get('request')}
        )
        return serializer.data


class FavoriteSerializer(serializers.Serializer):
    """Сериалайзер для добавления рецепта в избранное."""

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = self.context.get('recipe_id')
        if user.favorite.filter(recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в избранное'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = get_object_or_404(Recipe, pk=validated_data.get('id'))
        recipe.favorite.create(user=user)
        return RecipeListShortSerializer(
            instance=recipe, context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.Serializer):
    """Сериалайзер для добавления в корзину."""

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = self.context.get('recipe_id')
        if user.shoppingcart.filter(recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в список покупок'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = get_object_or_404(Recipe, pk=validated_data.get('id'))
        recipe.shoppingcart.create(user=user)
        return RecipeListShortSerializer(
            instance=recipe, context={'request': self.context.get('request')}
        ).data
