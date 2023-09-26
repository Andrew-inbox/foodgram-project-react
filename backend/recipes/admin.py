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
    """Ресурс модели рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'pub_date',
        )


class IngredientsInline(admin.TabularInline):
    """Встроенный класс для ингредиентов."""

    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    """Административный класс для рецепта."""

    resource_class = (RecipeResource,)
    inlines = (IngredientsInline,)
    list_display = (
        'id',
        'name',
        'author',
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author')

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('author')
            .prefetch_related('ingredients', 'tags')
        )


class TagResource(ModelResource):
    """Ресурс модели тегов."""

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
    """Модель ресурсов тегов администратора"""

    resource_class = (TagResource,)
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'color', 'slug')


class IngredientResource(ModelResource):
    """Ресурс для модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Класс для администрирования ингредиентов."""

    resource_classes = (IngredientResource,)
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


class RecipeIngredientResource(ModelResource):
    """Ресурс для модели ингредиентов рецепта."""

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
    """Класс для администрирования ингредиентов рецепта."""

    resource_classes = (RecipeIngredientResource,)
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe', 'ingredient')


class FavoriteResource(ModelResource):
    """Ресурс для модели избранных рецептов."""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(Favorite)
class FavoriteAdmin(ImportExportModelAdmin):
    """Класс для администрирования избранных рецептов."""

    resource_classes = (FavoriteResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('recipe')
            .prefetch_related('user')
        )


class ShoppingCartResource(ModelResource):
    """Ресурс для модели корзины покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe',
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ImportExportModelAdmin):
    """Класс для администрирования корзины покупок."""

    resource_classes = (ShoppingCartResource,)
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('recipe')
            .prefetch_related('user')
        )
