import logging
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserMetadata
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """A serializer to allow client to pass in 'refresh_token' instead of 'token'"""
    refresh_token = serializers.CharField(required=True)

    def to_internal_value(self, data):
        # Convert refresh_token to refresh before validation
        if 'refresh_token' in data:
            self._refresh_token = data['refresh_token']
            data = data.copy()
            data['refresh'] = data['refresh_token']
        return super().to_internal_value(data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """A serializer for creating new users"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        logger.info(f"New user registered: {user.email}")
        return user


class UserLoginSerializer(serializers.Serializer):
    """A serializer for a user logging in"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                logger.warning(f"Failed login attempt for email: {email}")
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """A generic serializer for a user profile"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')
