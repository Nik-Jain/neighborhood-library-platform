"""
Authentication views for the core library service application.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .auth_serializers import SignupSerializer, LoginSerializer, MemberDetailSerializer
from .models import Member, APIToken
from .protobuf_mixins import LoginProtobufMixin, SignupProtobufMixin
import secrets
import hashlib


class SignupView(SignupProtobufMixin, APIView):
    """
    API view for user signup/registration.
    POST: Create a new member account
    Supports both JSON and Protocol Buffer formats
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Create a new member account and return authentication token.
        """
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            
            # Get or create the Django User for this member (created by signal)
            user = User.objects.filter(username=member.email).first()
            if not user:
                # Fallback if signal didn't fire
                user = User.objects.create(
                    username=member.email,
                    email=member.email,
                    first_name=member.first_name,
                    last_name=member.last_name,
                    is_active=(member.membership_status == 'active')
                )
                user.set_unusable_password()
                user.save()
                # Assign MEMBER role
                from .utils import assign_default_member_role
                assign_default_member_role(user)
            
            # Create API token for the user
            token = APIToken.objects.create(user=user)
            
            return Response(
                {
                    'token': token.key,
                    'member': MemberDetailSerializer(member).data,
                    'message': 'Account created successfully'
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(LoginProtobufMixin, APIView):
    """
    API view for user login.
    POST: Authenticate user and return token
    Supports both JSON and Protocol Buffer formats
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
            
            # Get or create the Django User for this member
            user = User.objects.filter(username=member.email).first()
            if not user:
                # Create user if doesn't exist (shouldn't happen with signals)
                user = User.objects.create(
                    username=member.email,
                    email=member.email,
                    first_name=member.first_name,
                    last_name=member.last_name,
                    is_active=(member.membership_status == 'active')
                )
                user.set_unusable_password()
                user.save()
                from .utils import assign_default_member_role
                assign_default_member_role(user)
            
            # Get or create API token for this user
            token, created = APIToken.objects.get_or_create(user=user)
            
            return Response(
                {
                    'token': token.key,
                    'member': MemberDetailSerializer(member).data,
                    'message': 'Login successful'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


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
        # Delete all tokens for this user
        APIToken.objects.filter(user=request.user).delete()
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
        """
        user = request.user
        
        # Try to find the associated member
        try:
            member = Member.objects.get(email=user.username)
            return Response(
                {
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'groups': list(user.groups.values_list('name', flat=True)),
                    },
                    'member': MemberDetailSerializer(member).data,
                    'authenticated': True
                },
                status=status.HTTP_200_OK
            )
        except Member.DoesNotExist:
            return Response(
                {
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'groups': list(user.groups.values_list('name', flat=True)),
                    },
                    'authenticated': True
                },
                status=status.HTTP_200_OK
            )

