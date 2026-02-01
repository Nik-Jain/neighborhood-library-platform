"""
Authentication serializers for the core library service application.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Member
import uuid


class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup/registration.
    Creates a new Member account.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'password', 'password_confirm'
        ]
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return data
    
    def validate_email(self, value):
        """Validate email is unique."""
        if Member.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value
    
    def create(self, validated_data):
        """Create a new member account."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Generate a unique membership number
        membership_number = f"LIB-{uuid.uuid4().hex[:8].upper()}"
        
        member = Member.objects.create(
            membership_number=membership_number,
            **validated_data
        )
        
        # Store password as plain text (or you could hash it)
        # For now, we'll store it in a simple way
        member.set_password(password)
        member.save()
        
        return member


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Authenticates using email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate credentials and authenticate user."""
        email = data.get('email')
        password = data.get('password')
        
        # Try to find member by email
        try:
            member = Member.objects.get(email=email)
        except Member.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        
        # Verify password
        if not member.check_password(password):
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        
        # Check if membership is active
        if member.membership_status != 'active':
            raise serializers.ValidationError(
                "Your membership is not active. Please contact the library."
            )
        
        data['member'] = member
        return data


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for returning authentication token and user info.
    """
    token = serializers.CharField()
    member = serializers.SerializerMethodField()
    
    def get_member(self, obj):
        """Return member information."""
        from .serializers import MemberSerializer
        member = obj.get('member')
        return MemberSerializer(member).data


class MemberDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for returning member details after authentication.
    """
    full_name = serializers.CharField(read_only=True)
    active_borrowings_count = serializers.SerializerMethodField()
    overdue_borrowings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'address', 'membership_number', 'membership_status', 'join_date',
            'created_at', 'updated_at', 'active_borrowings_count',
            'overdue_borrowings_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'join_date']
    
    def get_active_borrowings_count(self, obj):
        """Get count of active borrowings."""
        return obj.get_active_borrowings().count()
    
    def get_overdue_borrowings_count(self, obj):
        """Get count of overdue borrowings."""
        return obj.get_overdue_borrowings().count()
