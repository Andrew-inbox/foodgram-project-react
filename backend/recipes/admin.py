from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeResource(ModelResource):
    """Модель ресурсов рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'pub_date',
        )


class IngredientsInline(admin.TabularInline):
    """Меню управления ингредиентами в рецепте."""

    model = IngredientAmount
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    """Регистрация модели рецептов и импорта/эскпорта в админ-панели."""

    resource_class = (RecipeResource,)
    inlines = (IngredientsInline,)
    list_display = (
        'id',
        'name',
        'author',
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author')


class TagResource(ModelResource):
    """Модель ресурсов тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    """Регистрация модели тегов и импорта/эскпорта в админ-панели."""

    resource_class = (TagResource,)
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'color', 'slug')


class IngredientResource(ModelResource):
    """Модель ресурсов ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Регистрация модели ингредиентов и импорта/эскпорта в админ-панели."""

    resource_classes = (IngredientResource,)
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


class IngredientAmountResource(ModelResource):
    """Модель ингредиента в рецепте."""

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'recipe',
            'ingredient',
            'amount',
        )


@admin.register(IngredientAmount)
class IngredientAmountAdmin(ImportExportModelAdmin):
    """
    Регистрация модели ингредиентов в рецепте и
    импорта/эскпорта в админ-панели.
    """

    resource_classes = (IngredientAmountResource,)
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe', 'ingredient')


class FavoriteResource(ModelResource):
    """Модель ресурсов избранных рецептов."""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(Favorite)
class FavoriteAdmin(ImportExportModelAdmin):
    """
    Регистрация модели избранных рецептов и импорта/эскпорта в админ-панели.
    """

    resource_classes = (FavoriteResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')


class ShoppingCartResource(ModelResource):
    """Модель ресурсов рецептов в корзине."""

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ImportExportModelAdmin):
    """
    Регистрация модели рецептов в корзине и импорта/эскпорта в админ-панели.
    """

    resource_classes = (ShoppingCartResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
