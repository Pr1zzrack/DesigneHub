from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('designes/', DesignerWorkViewSet.as_view({'get': 'list', 'post': 'create'}), name='designes'),
    path('designes/<int:id>/', DesignerWorkViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='designe'),
    path('register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('password-reset/', UserViewSet.as_view({'post': 'password_reset'}), name='password-reset'),
    path('password-reset-confirm/', UserViewSet.as_view({'post': 'password_reset_confirm'}), name='password-reset-confirm'),
    path('user-profile/', UserProfileViewSet.as_view({'get':'list', 'post':'create'}), name='user-profile'),
    path('user-profile/<int:id>/', UserProfileViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-profile'),
]
