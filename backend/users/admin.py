from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Административная панель для пользователей."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
    )
    list_filter = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('username')


class SubscribeResource(ModelResource):
    """Модель ресурсов подписок."""

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'user',
            'author',
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'author')


@admin.register(Subscribe)
class SubscribeAdmin(ImportExportModelAdmin):
    """Административная панель для модели подписок."""

    resource_class = (SubscribeResource,)
    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = (
        'author',
        'user',
    )
    search_fields = [
        'user__username',
        'user__username',
        'user__first_name',
        'user__last_name',
    ]
