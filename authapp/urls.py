from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccessRuleViewSet, ProductMockView, RegisterView, LoginView, LogoutView, RoleViewSet, UserProfileView, DeleteUserView

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'access-rules', AccessRuleViewSet, basename='access-rule')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('delete/', DeleteUserView.as_view(), name='delete'),
    path('products/', ProductMockView.as_view(), name='products'),
    path('admin/', include(router.urls)),
]