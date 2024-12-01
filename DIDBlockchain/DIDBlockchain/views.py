# Blockchain\DIDBlockchain\DIDBlockchain\views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.schemas import AutoSchema

class HomeView(APIView):
    permission_classes = [permissions.AllowAny] 
    schema = AutoSchema() 
    def get(self, request):
        # Create a response with the desired URLs
        response_data = {
            "admin": request.build_absolute_uri('/admin/'),
            "api": request.build_absolute_uri('/api/'),#restframework
            "docs": request.build_absolute_uri('/docs/'),
            "users/": request.build_absolute_uri('/users/'),#restframework 
            "webapp/": request.build_absolute_uri('/webapp/'),#GUI 
            "schema/": request.build_absolute_uri('/schema/')#GUI 
        }
        return Response(response_data, status=status.HTTP_200_OK)
