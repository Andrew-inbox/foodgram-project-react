from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserSetPasswordSerializer,
)
from .utils import create_shopping_list_pdf
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscribe, User


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('email', 'username')
    filterset_fields = ('email', 'username')

    def get_permissions(self):
        """Получение прав доступа для каждого действия."""
        permissions_dict = {
            'list': [permissions.IsAuthenticated()],
            'retrieve': [permissions.IsAuthenticated()],
            'me': [permissions.IsAuthenticated()],
            'set_password': [permissions.IsAuthenticated()],
            'subscriptions': [permissions.IsAuthenticated()],
            'subscribe': [permissions.IsAuthenticated()],
            'create': [permissions.AllowAny()],
        }
        return permissions_dict.get(
            self.action, [permissions.IsAuthenticated()]
        )

    def get_serializer_class(self):
        """Получение класса сериализатора для каждого действия."""
        serializer_class_dict = {
            'create': UserCreateSerializer,
            'list': UserListSerializer,
            'retrieve': UserListSerializer,
            'me': UserListSerializer,
            'set_password': UserSetPasswordSerializer,
            'subscriptions': SubscriptionSerializer,
            'subscribe': SubscribeSerializer,
        }
        return serializer_class_dict.get(self.action)

    @action(['GET'], detail=False)
    def me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(['POST'], detail=False)
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        old_password = serializer.validated_data.get('current_password')

        if not user.check_password(old_password):
            return Response(
                data='Неверный пароль', status=status.HTTP_400_BAD_REQUEST
            )
        if new_password == old_password:
            return Response(
                data='Пароли не должны совпадать',
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(
            data='Пароль успешно изменен', status=status.HTTP_204_NO_CONTENT
        )

    @action(['GET'], detail=False)
    def subscriptions(self, request):
        """Получение списка подписчиков текущего пользователя."""
        user = request.user
        subscribers = User.objects.filter(subscribed__user=user)
        page = self.paginate_queryset(subscribers)
        serializer = self.get_serializer(
            instance=page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk=None):
        """Подписка на пользователя."""
        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request, 'id': pk}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(data=response_data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            user = self.request.user
            subscribe, created = Subscribe.objects.filter(
                user=user, author_id=pk
            ).delete()

            if subscribe > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Подписка не найдена'},
                status=status.HTTP_404_NOT_FOUND,
            )


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели тэги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингридиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для модели рецепты."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return (
            Recipe.objects.select_related('author')
            .prefetch_related('tags', 'ingredients')
            .all()
        )

    def get_permissions(self):
        """Возвращает права доступа в зависимости от действия."""

        permissions_dict = {
            'create': [permissions.IsAuthenticated()],
            'partial_update': [permissions.IsAuthenticated()],
            'favorite': [permissions.IsAuthenticated()],
            'shopping_cart': [permissions.IsAuthenticated()],
            'download_shopping_cart': [permissions.IsAuthenticated()],
            'list': [permissions.AllowAny()],
            'retrieve': [permissions.AllowAny()],
        }
        return permissions_dict.get(
            self.action, [permissions.IsAuthenticated()]
        )

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""

        serializer_class_dict = {
            'create': RecipeCreateSerializer,
            'partial_update': RecipeCreateSerializer,
            'download_shopping_cart': RecipeCreateSerializer,
            'list': RecipeListSerializer,
            'retrieve': RecipeListSerializer,
            'favorite': FavoriteSerializer,
            'shopping_cart': ShoppingCartSerializer,
        }
        return serializer_class_dict.get(self.action, RecipeCreateSerializer)

    def perform_create(self, serializer):
        """Создает объект рецепта и присваивает ему автора."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Обновляет объект рецепта и присваивает ему автора."""
        serializer.save(author=self.request.user)

    @action(['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk=None):
        """Добавляет или удаляет рецепт из избранного."""

        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'recipe_id': pk},
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            user = self.request.user
            recipe = Recipe.objects.filter(pk=pk)
            favorite, created = Favorite.objects.filter(
                user=user, recipe=recipe
            ).delete()

            if favorite > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'В избранном рецепта нет'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из списка покупок."""

        if self.request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'recipe_id': pk},
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            user = self.request.user
            recipe = Recipe.objects.filter(pk=pk)
            shoppingcart, created = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).delete()

            if shoppingcart > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'В корзине рецепта нет'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(['GET'], detail=False)
    def download_shopping_cart(self, request):
        """Скачивает список покупок в формате PDF."""
        shopping_cart = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .order_by('ingredient__name')
            .annotate(ingredient_amount_sum=Sum('amount'))
        )
        buy_list_pdf = create_shopping_list_pdf(shopping_cart)
        response = HttpResponse(buy_list_pdf, content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping-list.pdf'
        return response
