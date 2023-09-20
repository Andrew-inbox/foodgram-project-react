# Generated by Django 4.2.5 on 2023-09-19 07:13

import colorfield.fields

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'избранный',
                'verbose_name_plural': 'Избранные',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=20, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Ингредиентов не может быть меньше 1!'), django.core.validators.MaxValueValidator(limit_value=50000, message='Ингредиентов не может быть больше 50000!')], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'количество ингредиента',
                'verbose_name_plural': 'Количество ингредиентов',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Фотограция')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('text', models.TextField(error_messages={'blank': 'Это поле обязательно для заполнения.', 'invalid': 'Введите корректное текстовое описание.'}, verbose_name='Текстовое описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Время приготовления не может быть меньше 1 минуты!'), django.core.validators.MaxValueValidator(limit_value=1000, message='Время приготовления не может быть больше 1000 минут!')], verbose_name='Время приготовления в минутах')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Название')),
                ('color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=7, samples=None, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Индентификатор')),
            ],
            options={
                'verbose_name': 'тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'корзина',
                'verbose_name_plural': 'Корзины',
            },
        ),
    ]
