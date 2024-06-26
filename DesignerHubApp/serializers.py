from rest_framework import serializers
from .models import *
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Поля пароля не совпали"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

class DesigneWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignerWork
        fields = ['id', 'user', 'media_data', 'hashtag', 'category', 'descriptions', 'views', 'likes']
        read_only_fields = ['user', 'views', 'likes']

class UserDesignViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = '__all__'

class UserSocialNetworkLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialNetworkLink
        fields = ['social_network_title', 'link_to_social_networks']

class UserContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactData
        fields = ['contact_title', 'contact_data']

class UserProfileSerializer(serializers.ModelSerializer):
    social_networks = UserSocialNetworkLinkSerializer(many=True)
    contact_data = UserContactDataSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'user_descriptions', 'social_networks', 'contact_data']
        read_only_fields = ['id', 'like_designs', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        else:
            raise serializers.ValidationError("Пользователь должен пройти аутентификацию для создания профиля")

        social_networks_data = validated_data.pop('social_networks', [])
        contact_data = validated_data.pop('contact_data', [])

        profile = UserProfile.objects.create(user=user, **validated_data)

        for social_network_data in social_networks_data:
            UserSocialNetworkLink.objects.create(user=profile, **social_network_data)

        for contact_data_item in contact_data:
            UserContactData.objects.create(user=profile, **contact_data_item)

        return profile

