from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema
from users.serializers import UserSerializer, UserRegisterSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegisterSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'register':
            return [AllowAny()]
        return [IsAdminUser()]
