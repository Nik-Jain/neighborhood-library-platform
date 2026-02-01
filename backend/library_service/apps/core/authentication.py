"""
Custom authentication backends for the library service.
"""
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class APITokenAuthentication(TokenAuthentication):
    """
    Token-based authentication using APIToken model.
    Returns the Django User associated with the token.
    """
    keyword = 'Token'
    model = None  # We'll import dynamically to avoid circular imports

    def authenticate_credentials(self, key):
        """
        Authenticate the token key and return the associated User.
        """
        # Import here to avoid circular dependency
        from .models import APIToken

        try:
            token = APIToken.objects.select_related('user').get(key=key)
        except APIToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User account is disabled.')

        # Update last_used_at timestamp
        token.last_used_at = timezone.now()
        token.save(update_fields=['last_used_at'])

        return (token.user, token)
