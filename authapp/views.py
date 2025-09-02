from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import status

from authapp.services.authentication import PasswordAuthentication

from .models import AccessRule, User, Role
from .serializers import (
    AccessRuleSerializer, LoginResponseSerializer, LogoutSerializer, 
    RoleSerializer, TokenPairSerializer, UserRegisterSerializer, 
    UserLoginSerializer, UserSerializer
)
from .services import JWTService, JWTAuthentication
from .permissions import HasPermission


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Пользователь зарегестирован'})
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request) -> Response:
        login_serializer = UserLoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)
            
        
        user_instance = PasswordAuthentication.authenticate_user(
            email=login_serializer.validated_data['email'],
            password=login_serializer.validated_data['password'],
            user_model=User
        )

        if not user_instance:
            return Response({"detail": "Неверные учетные данные"}, status=401)
        
        tokens = JWTService.generate_token_pair({
            'id': user_instance.id,
            'email': user_instance.email
        })

        response_serializer = LoginResponseSerializer({
            'user': user_instance,
            'tokens': tokens,
            'message': 'Успешная авторизация'
        })
        return Response(response_serializer.data, status=200)

class LogoutView(APIView):
    permission_classes = [HasPermission]
    def post(self, request) -> Response:
        logout_serializer = LogoutSerializer(data=request.data)
        logout_serializer.is_valid(raise_exception=True)

        refresh_token = logout_serializer.validated_data['refresh_token']
        
        success = JWTService.blacklist_refresh_token(refresh_token)
        if success:
            return Response({'message': 'Успешный выход из системы'}, status=205)
        else:
            return Response({'message':'Токен, уже занесенный в черный список или недействительный'}, status=400)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [HasPermission]
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return self.request.user

class DeleteUserView(APIView):
    permission_classes = [HasPermission]

    def delete(self, request) -> Response:
        user = request.user
        user.soft_delete()
        return Response({'message': 'Пользователь удален'}, status=200)

class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class AccessRuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

class ProductMockView(APIView):
    permission_classes = [HasPermission]
    business_element = 'product'

    def get(self, request) -> Response:
        product = {"id": 1, "name": "Продукт 1", "owner": request.user.id}

        self.check_object_permissions(request, product)

        return Response(product, status=200)

        








        