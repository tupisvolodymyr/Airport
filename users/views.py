from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
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

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)