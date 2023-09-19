from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .models import Ingredient, RecipeIngredient, Recipe, Tag
from .validators import (
    RecipeIngredientFieldValidator,
    ColorFieldValidator,
    CookingTimeRecipeFieldValidator,
)
from users.serializers import UserListSerializer


class TagSerializer(serializers.ModelSerializer):
    """"""

    color = ColorFieldValidator()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """"""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientAddSerializer(serializers.ModelSerializer):
    """"""

    id = serializers.IntegerField(source='ingredient.id')
    amount = RecipeIngredientFieldValidator()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeListShortSerializer(serializers.ModelSerializer):
    """"""

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    """"""

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
        if user.is_anonymous:
            return None
        return recipe.shoppingcart.filter(user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """"""

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

    def set_ingredients(self, recipe, ingredients_data):
        ingredients = list()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').get('id')
            amount = ingredient_data.get('amount')
            ingredient = Ingredient.objects.get(id=ingredient_id)

            if RecipeIngredient.objects.filter(
                recipe=recipe, ingredient=ingredient_id
            ).exists():
                amount += F('amount')
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
    """"""

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
    """"""

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
