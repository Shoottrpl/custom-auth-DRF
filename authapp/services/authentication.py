from typing import Optional, Dict, Any, Type
from django.contrib.auth.hashers import check_password
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.request import Request

from authapp.models import User
from authapp.services.jwt_service import JWTService
from authapp.exceptions import InvalidCredentialsError, InactiveUserError


class PasswordAuthentication:
    @staticmethod
    def authenticate_user(email: str, password: str, user_model: Type[User]) -> Optional[User]:
        user = user_model.objects.get(email=email)

        if not user.is_active:
            raise InactiveUserError()
        
        if not user or not check_password(password, user.password):
            raise InvalidCredentialsError()

        return user

    @staticmethod
    def authenticate_user_by_id(user_id: int, user_model: Type[User]) -> Optional[Dict[str, Any]]:
        try:
            user = user_model.objects.get(id=user_id)

            if not user.is_active:
                return None

            return {
                "user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.name if user.role else None,
                "role_id": user.role.id if user.role else None,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }

        except user_model.DoesNotExist:
            return None

    @staticmethod
    def check_user_permissions(user_data: Dict[str, Any], required_permissions: list) -> bool:
        if not user_data or not user_data.get('is_active'):
            return False

        if user_data.get('is_superuser'):
            return True

        return True

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> Optional[tuple[User, str]]:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not isinstance(auth_header, str):
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]
        payload = JWTService.verify_token(token)
        if not payload:
            raise exceptions.AuthenticationFailed("Недействительный или просроченный токен")

        user_id = payload.get('id')
        email = payload.get('email')

        try:
            user = User.objects.get(id=user_id, email=email, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Пользователь не найден или не активен")
        
        return (user, token)
                
