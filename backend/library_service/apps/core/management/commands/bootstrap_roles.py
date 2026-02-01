"""
Django management command to bootstrap roles (groups) and create a super admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Create default RBAC groups and a super admin user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@library.local')
        parser.add_argument('--password', type=str, default='admin123')

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Create groups
        for name in ('ADMIN', 'LIBRARIAN', 'MEMBER'):
            Group.objects.get_or_create(name=name)
            self.stdout.write(self.style.SUCCESS(f'Ensured group: {name}'))

        # Create superuser if not exists
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists'))

        # Ensure superuser is in ADMIN group
        admin_user = User.objects.filter(username=username).first()
        if admin_user:
            admin_group = Group.objects.get(name='ADMIN')
            admin_user.groups.add(admin_group)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Added {username} to ADMIN group'))

        # Sync existing Members to Users (for backward compatibility)
        self._sync_members_to_users()

        self.stdout.write(self.style.SUCCESS('RBAC bootstrap complete'))

    def _sync_members_to_users(self):
        """Create Django Users for existing Members that don't have one."""
        from library_service.apps.core.models import Member
        from library_service.apps.core.utils import assign_default_member_role

        members_without_users = []
        for member in Member.objects.all():
            if member.email and not User.objects.filter(username=member.email).exists():
                members_without_users.append(member)

        if not members_without_users:
            self.stdout.write(self.style.SUCCESS('All members already have Django User accounts'))
            return

        for member in members_without_users:
            try:
                user = User.objects.create(
                    username=member.email,
                    email=member.email,
                    first_name=member.first_name or '',
                    last_name=member.last_name or '',
                    is_active=(member.membership_status == 'active')
                )
                user.set_unusable_password()
                user.save()
                assign_default_member_role(user)
                self.stdout.write(self.style.SUCCESS(f'Created User for member: {member.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create User for {member.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Synced {len(members_without_users)} members to Users'))
