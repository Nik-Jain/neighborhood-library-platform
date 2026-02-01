"""
Utility helpers for role management.
"""
from django.contrib.auth.models import Group, User
from django.db import transaction
from typing import Optional


def get_or_create_group(name: str) -> Group:
    """Get or create a Group by name."""
    group, _ = Group.objects.get_or_create(name=name)
    return group


@transaction.atomic
def assign_default_member_role(user: Optional[User]):
    """Assign the `MEMBER` role to the given Django `User`.

    Safe to call with `None` — does nothing in that case.
    """
    if not user:
        return
    member_group = get_or_create_group('MEMBER')
    user.groups.add(member_group)
    user.save()


def ensure_roles_exist():
    """Ensure the standard roles exist: ADMIN, LIBRARIAN, MEMBER."""
    for name in ('ADMIN', 'LIBRARIAN', 'MEMBER'):
        get_or_create_group(name)
