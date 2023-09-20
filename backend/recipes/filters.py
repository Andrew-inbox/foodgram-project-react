from django_filters import rest_framework as filters

from users.models import User

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр для модели ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для модели рецептов."""

    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        """ Фильтрация избранных рецептов."""
        if value:
            return queryset.filter(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """ Фильтрация рецептов в корзине покупок."""
        if value:
            return queryset.filter(shoppingcart__user=self.request.user)
