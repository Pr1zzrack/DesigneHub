from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import *
from .serializers import *
from .filters import *
from django_filters import rest_framework as filters
from rest_framework_simplejwt.authentication import JWTAuthentication


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
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
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

class DesignerWorkViewSet(viewsets.ModelViewSet, filters.FilterSet):
    queryset = DesignerWork.objects.all()
    serializer_class = DesigneWorkSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DesignerWorkFilter

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

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
