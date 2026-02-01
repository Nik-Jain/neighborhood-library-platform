"""
Unit tests for RBAC permission classes.
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response

from library_service.apps.core.permissions import (
    IsAdmin,
    IsLibrarian,
    IsAdminOrLibrarian,
    IsMember,
)


class MockView(APIView):
    """Mock view for testing permissions."""
    def get(self, request):
        return Response({'message': 'success'})


class PermissionClassesTestCase(TestCase):
    """Test cases for RBAC permission classes."""

    def setUp(self):
        """Set up test users and groups."""
        self.factory = APIRequestFactory()
        
        # Create groups
        self.admin_group = Group.objects.create(name='ADMIN')
        self.librarian_group = Group.objects.create(name='LIBRARIAN')
        self.member_group = Group.objects.create(name='MEMBER')
        
        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='pass')
        self.admin_user.groups.add(self.admin_group)
        
        self.librarian_user = User.objects.create_user(username='librarian', password='pass')
        self.librarian_user.groups.add(self.librarian_group)
        
        self.member_user = User.objects.create_user(username='member', password='pass')
        self.member_user.groups.add(self.member_group)
        
        self.no_group_user = User.objects.create_user(username='nogroup', password='pass')
        
        self.view = MockView.as_view()

    def test_is_admin_permission_allows_admin(self):
        """Test IsAdmin allows users in ADMIN group."""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        permission = IsAdmin()
        self.assertTrue(permission.has_permission(request, MockView))

    def test_is_admin_permission_denies_non_admin(self):
        """Test IsAdmin denies users not in ADMIN group."""
        request = self.factory.get('/')
        request.user = self.librarian_user
        
        permission = IsAdmin()
        self.assertFalse(permission.has_permission(request, MockView))

    def test_is_admin_permission_denies_member(self):
        """Test IsAdmin denies MEMBER users."""
        request = self.factory.get('/')
        request.user = self.member_user
        
        permission = IsAdmin()
        self.assertFalse(permission.has_permission(request, MockView))

    def test_is_librarian_permission_allows_librarian(self):
        """Test IsLibrarian allows users in LIBRARIAN group."""
        request = self.factory.get('/')
        request.user = self.librarian_user
        
        permission = IsLibrarian()
        self.assertTrue(permission.has_permission(request, MockView))

    def test_is_librarian_permission_denies_non_librarian(self):
        """Test IsLibrarian denies users not in LIBRARIAN group."""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        permission = IsLibrarian()
        self.assertFalse(permission.has_permission(request, MockView))

    def test_is_admin_or_librarian_allows_admin(self):
        """Test IsAdminOrLibrarian allows ADMIN users."""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        permission = IsAdminOrLibrarian()
        self.assertTrue(permission.has_permission(request, MockView))

    def test_is_admin_or_librarian_allows_librarian(self):
        """Test IsAdminOrLibrarian allows LIBRARIAN users."""
        request = self.factory.get('/')
        request.user = self.librarian_user
        
        permission = IsAdminOrLibrarian()
        self.assertTrue(permission.has_permission(request, MockView))

    def test_is_admin_or_librarian_denies_member(self):
        """Test IsAdminOrLibrarian denies MEMBER users."""
        request = self.factory.get('/')
        request.user = self.member_user
        
        permission = IsAdminOrLibrarian()
        self.assertFalse(permission.has_permission(request, MockView))

    def test_is_member_permission_allows_member(self):
        """Test IsMember allows users in MEMBER group."""
        request = self.factory.get('/')
        request.user = self.member_user
        
        permission = IsMember()
        self.assertTrue(permission.has_permission(request, MockView))

    def test_is_member_permission_denies_non_member(self):
        """Test IsMember denies users not in MEMBER group."""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        permission = IsMember()
        self.assertFalse(permission.has_permission(request, MockView))

    def test_permissions_deny_unauthenticated(self):
        """Test all permissions deny unauthenticated users."""
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        permissions = [IsAdmin(), IsLibrarian(), IsAdminOrLibrarian(), IsMember()]
        for permission in permissions:
            self.assertFalse(
                permission.has_permission(request, MockView),
                f"{permission.__class__.__name__} should deny anonymous users"
            )

    def test_permissions_deny_user_with_no_groups(self):
        """Test all permissions deny users with no groups."""
        request = self.factory.get('/')
        request.user = self.no_group_user
        
        permissions = [IsAdmin(), IsLibrarian(), IsAdminOrLibrarian(), IsMember()]
        for permission in permissions:
            self.assertFalse(
                permission.has_permission(request, MockView),
                f"{permission.__class__.__name__} should deny users with no groups"
            )
