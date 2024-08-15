from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters import rest_framework as filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserBalanceSerializer
from .permissions import *
from .models import *
from .serializers import *
from .filters import *


User = get_user_model()

class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description='Пользователь успешно зарегистрирован',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: 'Неправильные данные для регистрации',
        },
        operation_description='Регистрация нового пользователя.',
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Регистрация нового пользователя.

        Параметры:
        - `email` (строка): Email пользователя.
        - `first_name` (строка): Имя пользователя.
        - `last_name` (строка): Фамилия пользователя.
        - `password` (строка): Пароль пользователя.

        Ответы:
        - 201: Пользователь успешно зарегистрирован.
        - 400: Неправильные данные для регистрации.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'status': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description='Успешный вход в систему',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING, default=''),
                                'user_descriptions': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                                'social_networks': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING)
                                ),
                                'contact_data': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING)
                                ),
                            }
                        ),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: 'Неправильный email или пароль',
        },
        operation_description='Вход в систему',
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            user_data = CustomUser.objects.get(email=user.email)
            user_profile_data1 = UserProfileSerializer(user_data.id).data
            user_profile_data2 = UserSerializer(user).data
            user_profile_data2.update(user_profile_data1)
            return Response({'user': user_profile_data2, 'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response({'detail': 'Неправильный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)


    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        responses={
            200: 'Ссылка для сброса пароля отправлена на указанный email',
            400: 'Неправильный email'
        },
        operation_description='Запрос на сброс пароля',
    )
    @action(detail=False, methods=['post'])
    def password_reset(self, request):
        """
        Запрос на сброс пароля.

        Параметры:
        - `email` (строка): Email пользователя.

        Ответы:
        - 200: Ссылка для сброса пароля отправлена на указанный email.
        - 400: Неправильный email.
        """
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(user=user)
            send_mail(
                'Password Reset Request',
                f'Токен для сброса пароля: http://127.0.0.1:8000/password-reset-confirm/?token={token.token}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'detail': 'Ссылка для сброса пароля отправлена на указанный email'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь с таким email не найден'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: 'Пароль успешно изменен',
            400: 'Неправильный или просроченный токен'
        },
        operation_description='Подтверждение сброса пароля',
    )
    @action(detail=False, methods=['post'])
    def password_reset_confirm(self, request):
        """
        Подтверждение сброса пароля.

        Параметры:
        - `token` (строка): Токен для сброса пароля.
        - `new_password` (строка): Новый пароль пользователя.

        Ответы:
        - 200: Пароль успешно изменен.
        - 400: Неправильный или просроченный токен.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = PasswordResetToken.objects.get(token=serializer.validated_data['token'])
                if token.is_valid():
                    user = token.user
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    token.delete()
                    return Response({'detail': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)
                else:
                    token.delete()
                    return Response({'detail': 'Токен просрочен'}, status=status.HTTP_400_BAD_REQUEST)
            except PasswordResetToken.DoesNotExist:
                return Response({'detail': 'Неправильный токен'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserBalanceViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_balance = UserBalance.objects.get(user=request.user)
        except UserBalance.DoesNotExist:
            return Response({"error": "User balance not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserBalanceSerializer(user_balance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_balance = UserBalance.objects.get(user=request.user)
        except UserBalance.DoesNotExist:
            user_balance = UserBalance.objects.create(user=request.user, balance=0.00)

        user_balance.add_funds(amount)
        serializer = UserBalanceSerializer(user_balance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DesignerWorkViewSet(viewsets.ModelViewSet, filters.FilterSet):
    queryset = DesignerWork.objects.all()
    serializer_class = DesigneWorkSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DesignerWorkFilter
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        request_body=DesigneWorkSerializer,
        responses={201: DesigneWorkSerializer()},
        operation_description='Добавление работы дизайнера.',
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: DesigneWorkSerializer(many=True)},
        operation_description='Получение списка всех работ дизайнеров с возможностью фильтрации по названию работы, имени дизайнера, хэштегам, категории и дате публикации.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: DesigneWorkSerializer()},
        operation_description='Получение информации о работе дизайнера.',
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.is_authenticated:
            if not View.objects.filter(user=user, designe=instance).exists():
                instance.views += 1
                instance.save(update_fields=['views'])
                View.objects.create(user=user, designe=instance)
        else:
            return Response({"detail": "Вы не аутентифицированы"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=DesigneWorkSerializer,
        responses={200: DesigneWorkSerializer()},
        operation_description='Обновление работы дизайнера.',
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail': 'Вы не имеете права обновлять эту работу'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={204: 'Работа дизайнера успешно удалена'},
        operation_description='Удаление работы дизайнера.',
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail': 'Вы не имеете права удалять эту работу'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        user_id = self.kwargs.get('id')
        return UserProfile.objects.get(user_id=user_id)

    @swagger_auto_schema(
        responses={200: UserProfileSerializer(many=True)},
        operation_description='Получение списка профилей пользователей.',
    )
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={200: UserProfileSerializer()},
        operation_description='Получение информации о профиле пользователя.',
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={201: UserProfileSerializer()},
        operation_description='Создание профиля пользователя.',
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer()},
        operation_description='Обновление профиля пользователя.',
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail': 'Вы не имеете права обновлять этот профиль'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={204: 'Профиль пользователя успешно удален'},
        operation_description='Удаление профиля пользователя.',
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail': 'Вы не имеете права удалять этот профиль'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user.userprofile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(request.user.userprofile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class UserSocialNetworkLinkViewSet(viewsets.ModelViewSet):
    queryset = UserSocialNetworkLink.objects.all()
    serializer_class = UserSocialNetworkLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserSocialNetworkLinkSerializer,
        responses={201: UserSocialNetworkLinkSerializer()},
        operation_description='Добавление ссылки на социальную сеть пользователя.',
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: UserSocialNetworkLinkSerializer(many=True)},
        operation_description='Получение списка всех ссылок на социальные сети пользователей.',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: UserSocialNetworkLinkSerializer()},
        operation_description='Получение информации о ссылке на социальную сеть пользователя.',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class UserContactDataViewSet(viewsets.ModelViewSet):
    queryset = UserContactData.objects.all()
    serializer_class = UserContactDataSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserContactDataSerializer,
        responses={201: UserContactDataSerializer()},
        operation_description='Добавление контактных данных пользователя.',
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: UserContactDataSerializer(many=True)},
        operation_description='Получение списка всех контактных данных пользователей.',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: UserContactDataSerializer()},
        operation_description='Получение информации о контактных данных пользователя.',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        favorite, created = Favorite.objects.get_or_create(user=self.request.user)
        return favorite

    @swagger_auto_schema(
        responses={200: FavoriteSerializer()},
        operation_description='Получение списка избранных дизайнов пользователя.',
    )
    def list(self, request):
        favorite = self.get_object()
        serializer = self.get_serializer(favorite)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=AddFavoriteDesignSerializer,
        responses={200: 'Дизайн добавлен в избранные', 400: 'Ошибка валидации данных'},
        operation_description='Добавление дизайна в избранное.',
    )
    @action(detail=False, methods=['post'])
    def add_design(self, request):
        favorite = self.get_object()
        serializer = AddFavoriteDesignSerializer(data=request.data)
        if serializer.is_valid():
            design = serializer.validated_data['design_id']
            if not favorite.designs.filter(id=design.id).exists():
                favorite.designs.add(design)
                favorite.save()
                return Response({'status': 'Дизайн добавлен в избранные'}, status=status.HTTP_200_OK)
            return Response({'status': 'Этот дизайн уже есть в избранных'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=RemoveFavoriteDesignSerializer,
        responses={200: 'Дизайн удален из избранных', 400: 'Ошибка валидации данных'},
        operation_description='Удаление дизайна из избранного.',
    )
    @action(detail=False, methods=['post'])
    def remove_design(self, request):
        favorite = self.get_object()
        serializer = RemoveFavoriteDesignSerializer(data=request.data)
        if serializer.is_valid():
            design = serializer.validated_data['design_id']
            if favorite.designs.filter(id=design.id).exists():
                favorite.designs.remove(design)
                favorite.save()
                return Response({'status': 'Дизайн удален из избранных'}, status=status.HTTP_200_OK)
            return Response({'status': 'Такого дизайна нет в избранных'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        like, created = Like.objects.get_or_create(user=self.request.user)
        return like

    @swagger_auto_schema(
        responses={200: LikeSerializer()},
        operation_description='Получение списка лайкнутых дизайнов пользователя.',
    )
    def list(self, request):
        like = self.get_object()
        serializer = self.get_serializer(like)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=AddLikeDesignSerializer,
        responses={200: 'Лайк на работу дизайнера добавлен', 400: 'Ошибка валидации данных'},
        operation_description='Добавление лайка на работу дизайнера.',
    )
    @action(detail=False, methods=['post'])
    def add_design(self, request):
        like = self.get_object()
        serializer = AddLikeDesignSerializer(data=request.data)
        if serializer.is_valid():
            design = serializer.validated_data['design_id']
            if not like.designs.filter(id=design.id).exists():
                like.designs.add(design)
                like.save()
                return Response({'status': 'Вы поставили лайк на эту работу дизайнера'}, status=status.HTTP_200_OK)
            return Response({'status': 'Дизайн не найден'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=RemoveLikeDesignSerializer,
        responses={200: 'Лайк на работу дизайнера убран', 400: 'Ошибка валидации данных'},
        operation_description='Удаление лайка с работы дизайнера.',
    )
    @action(detail=False, methods=['post'])
    def remove_design(self, request):
        like = self.get_object()
        serializer = RemoveLikeDesignSerializer(data=request.data)
        if serializer.is_valid():
            design = serializer.validated_data['design_id']
            if like.designs.filter(id=design.id).exists():
                like.designs.remove(design)
                like.save()
                return Response({'status': 'Вы убрали лайк с этой работы дизайнера'}, status=status.HTTP_200_OK)
            return Response({'status': 'Дизайн не найден'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatViewSet(viewsets.ModelViewSet):
    """
    API для управления чатами
    """
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(
            models.Q(user1=self.request.user.user_profile) | 
            models.Q(user2=self.request.user.user_profile)
        )

    @swagger_auto_schema(
        operation_summary="Создать новый чат",
        operation_description="Создает новый чат между двумя пользователями",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user2': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID второго пользователя'),
            },
            required=['user2']
        ),
        responses={
            201: openapi.Response('Чат успешно создан'),
            400: openapi.Response('Нельзя создать чат с самим собой или чат уже существует между этими пользователями'),
        }
    )
    def perform_create(self, serializer):
        """
        Создание нового чата
        """
        user1 = self.request.user.user_profile
        user2_id = self.request.data.get('user2')
        
        try:
            user2 = UserProfile.objects.get(user=user2_id)
        except User.DoesNotExist:
            raise Response({"detail": "Второй пользователь не найден"}, status=status.HTTP_400_BAD_REQUEST)

        if user1 == user2:
            raise Response({"detail": "Нельзя создать чат с самим собой"}, status=status.HTTP_400_BAD_REQUEST)

        if Chat.objects.filter(user1=user1, user2=user2).exists() or Chat.objects.filter(user1=user2, user2=user1).exists():
            raise Response({"detail": "Чат уже существует между этими пользователями"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user1=user1, user2=user2)

class MessageViewSet(viewsets.ModelViewSet):
    """
    API для управления сообщениями
    """
    # queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.user_profile
        return Message.objects.filter(chat__in=Chat.objects.filter(
            models.Q(user1=user) | models.Q(user2=user)
        ))

    @swagger_auto_schema(
        operation_summary="Отправить новое сообщение",
        operation_description="Отправляет новое сообщение от текущего пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Текст сообщения'),
            },
            required=['content']
        ),
        responses={
            201: openapi.Response('Сообщение успешно отправлено'),
        }
    )
    def perform_create(self, serializer):
        """
        Отправка нового сообщения
        """
        serializer.save(sender=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        design_id = self.kwargs.get('design_id')
        try:
            DesignerWork.objects.get(id=design_id)
            return Review.objects.filter(design_id=design_id)
        except DesignerWork.DoesNotExist:
            raise NotFound("Дизайн не найден")

    def perform_create(self, serializer):
        design_id = self.kwargs.get('design_id')
        user = self.request.user
        serializer.save(user=user, design_id=design_id)