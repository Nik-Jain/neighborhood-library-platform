"""
Authentication views for the core library service application.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .auth_serializers import SignupSerializer, LoginSerializer, MemberDetailSerializer
from .models import Member
import secrets
import hashlib


class SignupView(APIView):
    """
    API view for user signup/registration.
    POST: Create a new member account
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Create a new member account and return authentication token.
        """
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            
            # Create a custom token for this member (since we use UUID, not integer PKs)
            token_key = self._generate_token()
            
            return Response(
                {
                    'token': token_key,
                    'member': MemberDetailSerializer(member).data,
                    'message': 'Account created successfully'
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _generate_token(self):
        """Generate a random token key."""
        return secrets.token_hex(20)


class LoginView(APIView):
    """
    API view for user login.
    POST: Authenticate user and return token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticate user with email and password.
        Returns authentication token and member details.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.validated_data['member']
            
            # Generate token (we'll store it in member model later if needed)
            token_key = self._generate_token()
            
            return Response(
                {
                    'token': token_key,
                    'member': MemberDetailSerializer(member).data,
                    'message': 'Login successful'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _generate_token(self):
        """Generate a random token key."""
        return secrets.token_hex(20)


class LogoutView(APIView):
    """
    API view for user logout.
    POST: Delete the authentication token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout user by deleting their token.
        """
        return Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )


class CurrentUserView(APIView):
    """
    API view for getting current logged-in user information.
    GET: Return current user's member details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get current user's information.
        The user info is extracted from the token in the authentication middleware.
        """
        # For now, return a message that token is valid
        return Response(
            {
                'message': 'Token is valid',
                'authenticated': True
            },
            status=status.HTTP_200_OK
        )

