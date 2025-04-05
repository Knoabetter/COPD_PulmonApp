from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes

# Basic test endpoint
class TestView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "message": "API is working!",
        })

# User info endpoint for authenticated users
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
        })

# Authentication status endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status(request):
    if request.user.is_authenticated:
        return Response({
            "isAuthenticated": True,
            "username": request.user.username,
        })
    return Response({"isAuthenticated": False})

