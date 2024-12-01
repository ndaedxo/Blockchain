# DIDBlockchain\apps\users\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserCreateView, UserDetailView, 
    UserUpdateView, UserDeleteView, UserListView, 
    
)

# Create a router and register the UserViewSet
router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),  
    path('create/', UserCreateView.as_view(), name='user-create'),  # POST only
    
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # GET only
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),  # PUT only
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),  # DELETE only
    path('api-auth/', include('rest_framework.urls', namespace='user-auth')),
]

