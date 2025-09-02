from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Role, BusinessElement, User, AccessRule
# Register your models here.

class AccessRoleRuleInline(admin.StackedInline):
    model = AccessRule
    extra = 0

@admin.register(Role)
class RoleAdmin(ModelAdmin):
    inlines = [AccessRoleRuleInline]
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(BusinessElement)
class BusinessElementAdmin(ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('email', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'role')}),
        ('Правав доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'created_at', 'updated_at')}),
    ) 

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )

    readonly_fields = ('last_login', 'created_at', 'updated_at')

@admin.register(AccessRule)
class AccessRuleAdmin(ModelAdmin):
    list_display = ('role', 'business_element', 'read_permission', 'update_permission', 'delete_permission')
    list_filter = ('role', 'business_element', 'read_permission', 'update_permission', 'delete_permission')
    search_fields = ('role__name', 'business_element__name')
    ordering = ('role__name', 'business_element__name')