from typing import Optional, Any
from rest_framework.permissions import BasePermission
from .models import AccessRule, BusinessElement


class HasPermission(BasePermission):
    def _get_access_rule(self, user: Any, view: Any) -> Optional[AccessRule]:
        if user.is_superuser:
            return None
        
        element_name = getattr(view, 'business_element', None)
        if not element_name:
            return None
        
        try:
            element = BusinessElement.objects.get(name=element_name)
            rule = AccessRule.objects.get(role=user.role, business_element=element)
            return rule
        except (BusinessElement.DoesNotExist, AccessRule.DoesNotExist):
            return None
    
    def _check_permission(
        self, 
        rule: Optional[AccessRule], 
        request_method: str, 
        check_owner: bool = False, 
        obj: Optional[Any] = None, 
        user: Optional[Any] = None
    ) -> bool:
        if rule is None:
            return True
        
        method_to_permission = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }

        base_permission = method_to_permission.get(request_method)
        if not base_permission:
            return False
        
        if getattr(rule, f'{base_permission}_all_permission', False):
            return True
        
        if getattr(rule, f'{base_permission}_permission', False):
            if check_owner and (hasattr(obj, 'owner') or isinstance(obj, dict)):
                owner = obj.owner if hasattr(obj, 'owner') else obj.get('owner')
                return owner == user.id
            else:
                return True
        
        return False

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user

        if not user.is_authenticated:
                return False 
        
        rule = self._get_access_rule(user, view)
        return self._check_permission(rule, request.method, check_owner=False)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        user = request.user

        rule = self._get_access_rule(user, view)
        return self._check_permission(rule, request.method, check_owner=True, obj=obj, user=user)
       

                

        

            