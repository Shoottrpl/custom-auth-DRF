import jwt 
import hashlib
import json
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from typing import Optional, Dict, Any

from authapp.exceptions import TokenBlackListError


class JWTService:
    ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    REFRESH_TOKEN_EXPIRE_DAYS = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    @staticmethod
    def _generate_token(
        user_data: dict, 
        token_type: str,
        expires_delta: timedelta
    ) -> str:
        if token_type not in ['access', 'refresh']:
            raise ValueError("Invalid token type. Allowed: 'access', 'refresh'")
        payload = {
            'id': user_data.get('id'),
            'email': user_data.get('email'),
            'token_type': token_type
        }
        try:
            expire = timezone.now() + expires_delta

            token_payload = payload.copy()
            token_payload.update({
                'exp': expire.timestamp(),
                'iat': timezone.now().timestamp()
            })

            token = jwt.encode(
                token_payload,
                settings.SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )

            return token
        
        except Exception as e:
            raise Exception(f"Ошибка генерации токена: {str(e)}")
    
    @staticmethod
    def _get_cache_key(token:str) -> str:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return f"blacklist:{token_hash}"

    @staticmethod
    def generate_access_token(user_data: dict) -> str:
        return JWTService._generate_token(
                user_data=user_data,
                token_type='access',
                expires_delta=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES
             )

    @staticmethod
    def generate_refresh_token(user_data: dict) -> str:
        return JWTService._generate_token(
                user_data=user_data,
                token_type='refresh',
                expires_delta=JWTService.REFRESH_TOKEN_EXPIRE_DAYS
             )
    
    @staticmethod
    def generate_token_pair(user_data: dict) -> Dict[str, Any]:
        try:
            access_token = JWTService.generate_access_token(user_data)
            refresh_token = JWTService.generate_refresh_token(user_data)

            expires_in = JWTService.ACCESS_TOKEN_EXPIRE_MINUTES.total_seconds()
            refresh_expires_in = JWTService.REFRESH_TOKEN_EXPIRE_DAYS.total_seconds()

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': int(expires_in),
                'refresh_expires_in': int(refresh_expires_in)
            }

        except Exception as e:
            raise Exception(f"Ошибка генерации пары токенов: {str(e)}")

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                exp_datetime = timezone.datetime.fromtimestamp(
                    exp_timestamp,
                    tz=timezone.utc
                )
                if timezone.now() > exp_datetime:
                    return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = JWTService.verify_token(refresh_token)
            if not payload:
                return None

            if payload.get('token_type') != 'refresh':
                return None
            
            user_data = {
                'id': payload.get('id'),
                'email': payload.get('email')
            }

            new_access_token = JWTService.generate_access_token(user_data)
            return new_access_token
        
        except Exception:
            return None

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload
        except Exception:
            return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        payload = JWTService.verify_token(token)
        return payload is None

    @staticmethod
    def blacklist_refresh_token(token:str) -> bool:
        try:
            if JWTService.is_token_blacklisted(token):
                return False
                
            payload = JWTService.verify_token(token)
            if not payload:
                return False
            
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                exp_datetime = timezone.datetime.fromtimestamp(
                        exp_timestamp,
                        tz=timezone.utc
                    )
                time_remaining = exp_datetime - timezone.now()
                ttl_seconds = max(0, int(time_remaining.total_seconds()))

                if ttl_seconds == 0:
                    return False
            else:
                ttl_seconds = JWTService.REFRESH_TOKEN_EXPIRE_DAYS

            cache_key = JWTService._get_cache_key(token)
            token_info = {
                'blacklisted_at': timezone.now().isoformat(),
                'token_type': payload.get('token_type', 'refresh'),
                'user_id': payload.get('id')
            }

            cache.set(cache_key, json.dumps(token_info), timeout=ttl_seconds)
            return True
        except TokenBlackListError:
            return False

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        try:
            cache_key = JWTService._get_cache_key(token)
            return cache.get(cache_key) is not None
        except TokenBlackListError:
            return False







        



