# DIDBlockchain\apps\users\views.py
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from django.urls import get_resolver
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

CustomUser = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def list_urls(self, request):
        url_list = []

        routes = [
            {'name': 'user-list', 'pattern': reverse('users-list', request=request)},
            {'name': 'user-create', 'pattern': reverse('user-create', request=request)},
            # {'name': 'user-login', 'pattern': reverse('user-login', request=request)},
            {'name': 'user-detail', 'pattern': reverse('user-detail', kwargs={'pk': 1}, request=request)},  # Example pk
            {'name': 'user-update', 'pattern': reverse('user-update', kwargs={'pk': 1}, request=request)},  # Example pk
            {'name': 'user-delete', 'pattern': reverse('user-delete', kwargs={'pk': 1}, request=request)},  # Example pk
        ]

        for route in routes:
            url_list.append({
                "name": route['name'],
                "pattern": route['pattern']
            })

        return Response(url_list)


    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def activate(self, request, pk=None):
        user = self.get_object()
        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_active:
            return Response({'status': 'user already active'}, status=status.HTTP_200_OK)

        user.is_active = True
        user.save()
        return Response({'status': 'user activated'}, status=status.HTTP_200_OK)

class UserCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        # Check if the user already exists
        username = request.data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'User already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().post(request, *args, **kwargs)

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)




class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

