from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        blank=False,
        max_length=254,
        validators=(
            EmailValidator(
                message='Некорректный e-mail!',
            ),
        ),
    )
    username = models.CharField(
        verbose_name='Username',
        unique=True,
        max_length=150,
        validators=(validate_username,),
    )
    password = models.CharField(
        verbose_name='Пароль',
        blank=False,
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'username',
                    'email',
                ),
                name='unique_username',
            ),
        )

    def __str__(self):
        return f'{self.username} ({self.email})'


class Subscribe(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribed',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'author',
                ),
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check_author',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
