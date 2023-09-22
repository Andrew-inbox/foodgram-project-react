from rest_framework import serializers
from webcolors import hex_to_name

from django.core.exceptions import ValidationError


def validate_colorfield(value):
    try:
        data = hex_to_name(value)
    except ValueError:
        raise ValidationError('Такого цвета нет!')
    return data


class ColorFieldValidator(serializers.Field):

    """Валидатор для проверки корректности цвета в формате HEX."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        """Проверяет корректность цвета в формате HEX."""
        try:
            data = hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Такого цвета нет!')
        return data


class CookingTimeRecipeFieldValidator(serializers.Field):

    """Валидатор для проверки корректности времени приготовления рецепта."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        """Проверяет корректность времени приготовления рецепта."""
        try:
            if 0 >= int(data) > 1000:
                raise serializers.ValidationError(
                    'Время приготовления должно быть больше 0 и не больше 1000'
                )
        except ValueError:
            raise serializers.ValidationError(
                'Время приготовления должно быть указано цифрой'
            )
        return data


class RecipeIngredientFieldValidator(serializers.Field):

    """Валидатор для проверки количества ингредиентов в рецепте."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):

        """Проверяет корректность количества ингредиентов в рецепте."""
        try:
            if 0 >= int(data) > 50000:
                raise serializers.ValidationError(
                    'Количество ингредиентов не может быть меньше 1 '
                    'и больше 5000'
                )
        except ValueError:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть указано цифрой'
            )
        return data
