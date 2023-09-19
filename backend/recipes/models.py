from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        db_index=True,
        blank=False,
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        blank=False,
        max_length=20,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название',
        unique=True,
        db_index=True,
        blank=False,
        max_length=200,
    )
    color = ColorField(
        format='hex',
        default='#FF0000',
        verbose_name='Цвет',
        unique=True,
        blank=False,
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name='Индентификатор',
        unique=True,
        blank=False,
        max_length=200,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    image = models.ImageField(
        verbose_name='Фотограция',
        upload_to='recipes/',
    )
    name = models.CharField(
        verbose_name='Название',
        blank=False,
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        blank=False,
        error_messages={
            'blank': 'Это поле обязательно для заполнения.',
            'invalid': 'Введите корректное текстовое описание.',
        },
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        blank=False,
        validators=(
            MinValueValidator(
                limit_value=1,
                message='Время приготовления не может быть меньше 1 минуты!',
            ),
            MaxValueValidator(
                limit_value=1000,
                message='Время приготовления не может быть больше 1000 минут!',
            ),
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name

    def clean(self):
        ingredients = self.ingredients.all()
        unique_ingredients = set()
        for ingredient in ingredients:
            if ingredient in unique_ingredients:
                raise ValidationError(
                    'Ингредиенты не должны дублироваться в рецепте'
                )
            unique_ingredients.add(ingredient)
        super().clean()


class IngredientAmount(models.Model):
    """Модель количества ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                limit_value=1, message='Ингредиентов не может быть меньше 1!'
            ),
            MaxValueValidator(
                limit_value=50000,
                message='Ингредиентов не может быть больше 50000!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}, {self.amount}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        verbose_name = 'избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='favorite_unique',
            ),
        )

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Модель для рецептов в корзины."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shoppingcart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shoppingcart',
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='shopping_cart_unique',
            ),
        )

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в корзину'
