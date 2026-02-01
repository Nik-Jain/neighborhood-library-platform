"""
DRF permission classes for role-based access control using Django Groups.
"""
from typing import Optional

from django.contrib.auth.models import Group, User
from rest_framework.permissions import BasePermission


def _user_in_group(user: Optional[User], group_name: str) -> bool:
    """Return True if the given user is a member of group_name.

    Works safely if `user` is None or not a Django `User` instance.
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    try:
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False


class IsAdmin(BasePermission):
    """Allow access only to users in the ADMIN group."""

    def has_permission(self, request, view):
        return _user_in_group(request.user, 'ADMIN')


class IsLibrarian(BasePermission):
    """Allow access only to users in the LIBRARIAN group."""

    def has_permission(self, request, view):
        return _user_in_group(request.user, 'LIBRARIAN')


class IsAdminOrLibrarian(BasePermission):
    """Allow access to users in ADMIN or LIBRARIAN groups."""

    def has_permission(self, request, view):
        return (
            _user_in_group(request.user, 'ADMIN')
            or _user_in_group(request.user, 'LIBRARIAN')
        )


class IsMember(BasePermission):
    """Allow access only to users in the MEMBER group."""

    def has_permission(self, request, view):
        return _user_in_group(request.user, 'MEMBER')
