from typing import Any, Dict
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from authapp.exceptions import InactiveUserError, InvalidCredentialsError
from authapp.models import AccessRule, User, Role
from authapp.services.authentication import PasswordAuthentication


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'role')

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        password = data.get('password')
        try:
            validate_password(password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        except Exception as e:
            raise serializers.ValidationError({"password": [str(e)]})
       
        if password != data.get('password2'):
            raise serializers.ValidationError({"password2": ["Пароли не совпадают"]})
            
        return data

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user = PasswordAuthentication.authenticate_user(
                email=data['email'], 
                password=data['password'],
                user_model=User
            )
        except InvalidCredentialsError:
            raise serializers.ValidationError({"non_field_errors": ["Неверные учетные данные"]})
        except InactiveUserError:
            raise serializers.ValidationError({"non_field_errors": ["Аккаунт деактивирован"]})
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active')

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class AccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRule
        fields = '__all__'
            
#JWT сериализаторы
class TokenPairSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    token_type = serializers.CharField(read_only=True, default='bearer')
    expires_in = serializers.IntegerField(read_only=True)
    refresh_expires_in = serializers.IntegerField(read_only=True)

class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    token_type = serializers.CharField(read_only=True, default='bearer')
    expires_in = serializers.IntegerField(read_only=True)

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

class UserTokenSerializer(serializers.ModelSerializer):
    tokens = TokenPairSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'tokens')

class LoginResponseSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    tokens = TokenPairSerializer(read_only=True)
    message = serializers.CharField(read_only=True, default="Успешная авторизация")

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    message = serializers.CharField(read_only=True, default="Успешный выход из системы")

class TokenRefreshResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    token_type = serializers.CharField(read_only=True, default='bearer')
    expires_in = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True, default="Токен обновлен")
