# Сервисы аутентификации и управления паролями

Этот пакет предоставляет разделенные сервисы для:
- Хэширования и валидации паролей
- Аутентификации пользователей (сравнение с БД)
- Работы с JWT токенами

## Архитектура

Сервисы разделены по ответственности:

### 1. PasswordService
Отвечает за работу с паролями:
- Хэширование паролей с bcrypt
- Проверка паролей
- Валидация сложности паролей

### 2. AuthService
Отвечает за аутентификацию пользователей:
- Сравнение учетных данных с БД
- Получение данных пользователя
- Проверка прав доступа

### 3. JWTService
Отвечает за работу с JWT токенами:
- Создание access и refresh токенов
- Проверка токенов
- Обновление токенов

## Основные компоненты

### PasswordService

```python
from authapp.services import PasswordService

# Хэширование пароля
hashed = PasswordService.hash_password("my_secure_password")

# Проверка пароля
is_valid = PasswordService.verify_password("my_secure_password", hashed)

# Валидация пароля
result = PasswordService.validate_password("weak_password")
if not result['is_valid']:
    print("Ошибки:", result['errors'])
```

### AuthService

```python
from authapp.services import AuthService
from authapp.models import UserModel

# Аутентификация пользователя (аналог вашего кода)
user_data = AuthService.authenticate_user("user@example.com", "password", UserModel)

if user_data:
    print(f"Пользователь: {user_data['first_name']} {user_data['last_name']}")

# Получение данных пользователя по ID
user_data = AuthService.authenticate_user_by_id(user_id, UserModel)

# Проверка прав доступа
has_permission = AuthService.check_user_permissions(user_data, ["read", "write"])
```

### JWTService

```python
from authapp.services import JWTService

# Создание токенов для пользователя
tokens = JWTService.create_tokens_for_user(user_data)

# Проверка токена
payload = JWTService.verify_token(token, "access")
if payload:
    user_id = payload['user_id']

# Обновление токена
new_token = JWTService.refresh_access_token(refresh_token)
```

## Пример использования (аналог вашего кода)

```python
from authapp.services import AuthService
from authapp.models import UserModel

async def authenticate(email: str, password: str) -> Optional[dict]:
    """
    Аутентификация пользователя (аналог вашего кода)
    """
    user_data = AuthService.authenticate_user(email, password, UserModel)
    
    if user_data:
        return {
            "user_id": user_data["user_id"],
            "full_name": f"{user_data['first_name']} {user_data['last_name']}",
            "email": user_data["email"],
            "role": user_data["role"],
        }
    return None
```

## API Endpoints

### 1. Регистрация пользователя
```
POST /api/auth/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password123",
    "first_name": "Иван",
    "last_name": "Петров"
}
```

### 2. Аутентификация
```
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password123"
}
```

### 3. Обновление токена
```
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh_token": "your_refresh_token_here"
}
```

### 4. Валидация пароля
```
POST /api/auth/validate-password/
Content-Type: application/json

{
    "password": "password_to_validate"
}
```

## Middleware

### JWTAuthenticationMiddleware

Автоматически проверяет JWT токены в заголовке `Authorization`.

**Использование:**
```python
# settings.py
MIDDLEWARE = [
    # ... другие middleware
    'authapp.middleware.JWTAuthenticationMiddleware',
    'authapp.middleware.RoleBasedAccessMiddleware',
]
```

**Формат заголовка:**
```
Authorization: Bearer <your_jwt_token>
```

## Преимущества разделения

1. **Принцип единственной ответственности**: Каждый сервис отвечает за свою область
2. **Переиспользование**: Можно использовать сервисы независимо
3. **Тестируемость**: Легче писать unit-тесты для каждого сервиса
4. **Гибкость**: Можно легко заменить один сервис на другой
5. **Читаемость**: Код более понятный и структурированный

## Примеры интеграции

### Простая аутентификация (как в вашем коде)
```python
from authapp.services import AuthService

def login(email: str, password: str):
    user_data = AuthService.authenticate_user(email, password, UserModel)
    if user_data:
        return {"user": user_data}
    return {"error": "Неверные учетные данные"}
```

### Аутентификация с токенами
```python
from authapp.services import AuthService, JWTService

def login_with_tokens(email: str, password: str):
    user_data = AuthService.authenticate_user(email, password, UserModel)
    if user_data:
        tokens = JWTService.create_tokens_for_user(user_data)
        return {"user": user_data, "tokens": tokens}
    return {"error": "Неверные учетные данные"}
```

### Регистрация с валидацией
```python
from authapp.services import PasswordService, AuthService, JWTService

def register(email: str, password: str, first_name: str, last_name: str):
    # Валидация пароля
    validation = PasswordService.validate_password(password)
    if not validation["is_valid"]:
        return {"error": validation["errors"]}
    
    # Хэширование пароля
    hashed_password = PasswordService.hash_password(password)
    
    # Создание пользователя
    user = UserModel.objects.create(
        email=email,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Получение данных и создание токенов
    user_data = AuthService.authenticate_user_by_id(user.id, UserModel)
    tokens = JWTService.create_tokens_for_user(user_data)
    
    return {"user": user_data, "tokens": tokens}
```
