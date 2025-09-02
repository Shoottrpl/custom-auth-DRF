from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from typing import Optional, Any


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
    
    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"


class Role(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

class BusinessElement(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Бизнес элементы'
        verbose_name_plural = 'Бизнес элементы'

class AccessRule(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')
    business_element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, verbose_name='Бизнес элемент')
    read_permission = models.BooleanField(default=False, verbose_name='Право на просмотр')
    read_all_permission = models.BooleanField(default=False, verbose_name='Право на просмотр всех')
    create_permission = models.BooleanField(default=False, verbose_name='Право на создание')
    update_permission = models.BooleanField(default=False, verbose_name='Право на изменение')
    update_all_permission = models.BooleanField(default=False, verbose_name='Право на изменение всех')
    delete_permission = models.BooleanField(default=False, verbose_name='Право на удаление')
    delete_all_permission = models.BooleanField(default=False, verbose_name='Право на удаление всех')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'business_element'],
                name='unique_role_business_element'
                )
        ]
        verbose_name = 'Правила доступа'
        verbose_name_plural = 'Правила доступа'
        

class UserManager(BaseUserManager):
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name='Роль')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def soft_delete(self) -> None:
        self.is_active = False
        self.save()

    def has_perm(self, perm: str, obj: Optional[Any] = None) -> bool:
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label: str) -> bool:
        return self.is_superuser or super().has_module_perms(app_label)

    def __str__(self) -> str:
        return self.email
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'





    

