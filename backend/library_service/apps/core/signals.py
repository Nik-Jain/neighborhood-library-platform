"""
Signals to keep Django `User` rows in sync with `Member` model and assign default roles.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Member
from .utils import assign_default_member_role


@receiver(post_save, sender=Member)
def create_or_update_user_for_member(sender, instance: Member, created, **kwargs):
    """Create or update a `User` corresponding to a `Member`.

    - Creates a Django `User` with `username=member.email` if none exists.
    - Marks account active/inactive based on `membership_status`.
    - Assigns the `MEMBER` group to new users.

    This keeps RBAC groups attached to Django `User` objects while preserving
    the existing `Member` model as the primary domain model for library members.
    """
    if not instance.email:
        return

    username = instance.email
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            # Create a lightweight user so we can assign groups
            user = User.objects.create(
                username=username,
                first_name=instance.first_name or '',
                last_name=instance.last_name or '',
                email=instance.email,
                is_active=(instance.membership_status == 'active')
            )
            # Do not try to reuse Member.password hash; set unusable password
            user.set_unusable_password()
            user.save()
            assign_default_member_role(user)
        else:
            # Keep active state in sync
            is_active = (instance.membership_status == 'active')
            if user.is_active != is_active:
                user.is_active = is_active
                user.save()
    except Exception:
        # Be defensive in signals — avoid bubbling errors during save
        pass
