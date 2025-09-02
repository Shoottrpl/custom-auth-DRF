# Система аутентификации и авторизации

Собственная система управления доступом к ресурсам, реализованная на Django + DRF с использованием JWT токенов и кастомной системы ролей и разрешений.

## Архитектура системы

### Основные компоненты
- **Аутентификация**: JWT токены, bcrypt для хэширования паролей
- **Авторизация**: Кастомная система ролей и правил доступа
- **Permissions**: Проверка прав доступа к бизнес-объектам

## Логика авторизации

### Принцип работы
1. **Аутентификация**: Пользователь получает JWT токен при логине
3. **Permissions**: Проверяются права доступа к конкретному бизнес-объекту
4. **Доступ**: Если права есть - ресурс выдается, если нет - ошибка 403

### Типы разрешений
- `read_permission` - чтение собственных объектов
- `read_all_permission` - чтение всех объектов
- `create_permission` - создание объектов
- `update_permission` - изменение собственных объектов
- `update_all_permission` - изменение всех объектов
- `delete_permission` - удаление собственных объектов
- `delete_all_permission` - удаление всех объектов

## Описание работы Permissions

**Принцип работы:**
1. Проверяет аутентификацию пользователя
2. Определяет бизнес-объект из view
3. Находит правило доступа для роли пользователя и объекта
4. Проверяет соответствующее разрешение в зависимости от HTTP метода

## API Endpoints

### Аутентификация

#### Регистрация
```http
POST /api/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "password2": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "middle_name": "Иванович",
    "role": 1
}
```

**Ответ:**
```json
{
    "message": "Пользователь зарегистрирован"
}
```

#### Логин
```http
POST /api/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**Ответ:**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Получение профиля
```http
GET /api/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Ответ:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "middle_name": "Иванович",
    "role": 1,
    "is_active": true
}
```

#### Обновление профиля
```http
PUT /api/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "first_name": "Петр",
    "last_name": "Петров"
}
```

#### Удаление пользователя
```http
DELETE /api/delete/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Админские эндпоинты (только для администраторов)

#### Управление ролями

**Получение списка ролей:**
```http
GET /api/admin/roles/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Создание роли:**
```http
POST /api/admin/roles/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "name": "Модератор"
}
```

**Обновление роли:**
```http
PUT /api/admin/roles/1/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "name": "Старший модератор"
}
```

**Удаление роли:**
```http
DELETE /api/admin/roles/1/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Управление бизнес-объектами

**Получение списка объектов:**
```http
GET /api/admin/business-elements/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Создание объекта:**
```http
POST /api/admin/business-elements/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "name": "invoice"
}
```

#### Управление правилами доступа

**Получение списка правил:**
```http
GET /api/admin/access-rules/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Создание правила:**
```http
POST /api/admin/access-rules/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "role": 2,
    "element": 1,
    "read_permission": true,
    "read_all_permission": false,
    "create_permission": true,
    "update_permission": true,
    "update_all_permission": false,
    "delete_permission": false,
    "delete_all_permission": false
}
```

### Бизнес-объекты (Mock Views)

#### Получение товаров
```http
GET /api/products/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Ответ (если есть права на чтение):**
```json
[
    {"id": 1, "name": "Товар 1", "owner": 1},
    {"id": 2, "name": "Товар 2", "owner": 2}
]
```

**Ответ (если нет прав):**
```json
{
    "detail": "У вас нет прав для выполнения этого действия."
}
```

## Коды ошибок

- **401 Unauthorized** - Пользователь не аутентифицирован
- **403 Forbidden** - Пользователь аутентифицирован, но нет прав доступа
- **400 Bad Request** - Неверные данные в запросе
- **404 Not Found** - Ресурс не найден

## Установка и запуск

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd simple_auth
```

2. **Запуск через Docker Compose:**
```bash
docker-compose up --build
```

3. **Создание суперпользователя:**
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Заполнение тестовыми данными:**
```bash
docker-compose exec web python manage.py shell
```
```python
from authapp.models import Role, BusinessElement, AccessRoleRule

# Создание ролей
admin_role = Role.objects.create(name='admin')
manager_role = Role.objects.create(name='manager')
user_role = Role.objects.create(name='user')

# Создание бизнес-объектов
product_element = BusinessElement.objects.create(name='product')
order_element = BusinessElement.objects.create(name='order')
user_element = BusinessElement.objects.create(name='user')

# Создание правил доступа
AccessRoleRule.objects.create(
    role=admin_role, element=product_element,
    read_permission=True, read_all_permission=True,
    create_permission=True, update_permission=True,
    update_all_permission=True, delete_permission=True,
    delete_all_permission=True
)
