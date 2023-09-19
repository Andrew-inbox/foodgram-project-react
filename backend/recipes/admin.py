from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeResource(ModelResource):
    """"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'pub_date',
        )


class IngredientsInline(admin.TabularInline):
    """"""

    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    """"""

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
    """"""

    resource_class = (TagResource,)
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'color', 'slug')


class IngredientResource(ModelResource):
    """"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """"""

    resource_classes = (IngredientResource,)
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


class RecipeIngredientResource(ModelResource):
    """"""

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'recipe',
            'ingredient',
            'amount',
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(ImportExportModelAdmin):
    """"""

    resource_classes = (RecipeIngredientResource,)
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe', 'ingredient')


class FavoriteResource(ModelResource):
    """"""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(Favorite)
class FavoriteAdmin(ImportExportModelAdmin):
    """"""

    resource_classes = (FavoriteResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')


class ShoppingCartResource(ModelResource):
    """"""

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ImportExportModelAdmin):
    """"""

    resource_classes = (ShoppingCartResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
