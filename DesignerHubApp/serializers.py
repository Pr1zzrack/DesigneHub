from rest_framework import serializers, generics
from rest_framework.exceptions import NotFound
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import *


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Поля пароля не совпали"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        
        UserProfile.objects.create(user=user)
        return user

class UserBalanceSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserBalance
            fields = '__all__'


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
            raise serializers.ValidationError({"password": "Второй пороль введен не верно"})
        return attrs

class DesigneWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignerWork
        fields = ['id', 'designe_title', 'user', 'media_data', 'hashtag', 'category', 'descriptions', 'views', 'likes']
        read_only_fields = ['user', 'views', 'likes']

    def validate(self, data):
        user = self.context['request'].user
        if not user.can_publish():
            raise serializers.ValidationError(f'Пользователь со статусом {user.status} не может публиковать больше работ в этом месяце.')
        return data

class UserDesignViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    designs = serializers.PrimaryKeyRelatedField(many=True, queryset=DesignerWork.objects.all())

    class Meta:
        model = Favorite
        fields = ['designs']

class AddFavoriteDesignSerializer(serializers.Serializer):
    design_id = serializers.PrimaryKeyRelatedField(queryset=DesignerWork.objects.all())

class RemoveFavoriteDesignSerializer(serializers.Serializer):
    design_id = serializers.PrimaryKeyRelatedField(queryset=DesignerWork.objects.all())

class LikeSerializer(serializers.ModelSerializer):
    designs = serializers.PrimaryKeyRelatedField(many=True, queryset=DesignerWork.objects.all())

    class Meta:
        model = Like
        fields = ['designs']

class AddLikeDesignSerializer(serializers.Serializer):
    design_id = serializers.PrimaryKeyRelatedField(queryset=DesignerWork.objects.all())

class RemoveLikeDesignSerializer(serializers.Serializer):
    design_id = serializers.PrimaryKeyRelatedField(queryset=DesignerWork.objects.all())

class UserSocialNetworkLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialNetworkLink
        # fields = ['id', 'social_network_title', 'link_to_social_networks']
        fields = '__all__'

class UserContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactData
        # fields = ['id', 'contact_title', 'contact_data']
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    social_networks = serializers.SerializerMethodField()
    contact_data = serializers.SerializerMethodField()
    user_first_name = serializers.CharField(source='user.first_name', required=False)
    user_last_name = serializers.CharField(source='user.last_name', required=False)
    user_email = serializers.StringRelatedField(source='user.email')
    user_status = serializers.StringRelatedField(source='user.status')

    class Meta:
        model = UserProfile
        fields = ['user', 'user_email', 'user_first_name', 'user_last_name', 'user_status', 'user_descriptions', 'user_profile_image', 'social_networks', 'contact_data']
        read_only_fields = ['user', 'user_email', 'user_status', 'social_networks', 'contact_data']
        extra_kwargs = {
            'user_descriptions': {'required': False},
            'user_profile_image': {'required': False},
        }

    def get_social_networks(self, obj):
        social_networks = UserSocialNetworkLink.objects.filter(user=obj)
        serializer = UserSocialNetworkLinkSerializer(social_networks, many=True)
        return serializer.data

    def get_contact_data(self, obj):
        contact_data = UserContactData.objects.filter(user=obj)
        serializer = UserContactDataSerializer(contact_data, many=True)
        return serializer.data

    def update(self, instance, validated_data):
        user = instance.user
        user.first_name = validated_data.get('user_first_name', user.first_name)
        user.last_name = validated_data.get('user_last_name', user.last_name)
        user.save()

        instance.user_descriptions = validated_data.get('user_descriptions', instance.user_descriptions)
        instance.user_profile_image = validated_data.get('user_profile_image', instance.user_profile_image)
        instance.save()
        
        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class UserProfileGetForChatSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfileGetForChatSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'timestamp']

class ChatSerializer(serializers.ModelSerializer):
    user1 = UserProfileGetForChatSerializer(read_only=True)
    user2 = UserProfileGetForChatSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user1', 'user2', 'messages']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user_first_name = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = Review
        fields = ['user_first_name', 'design', 'content', 'created_at']
        read_only_fields = ['user_first_name', 'design', 'created_at']

