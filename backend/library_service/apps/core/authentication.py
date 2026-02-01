"""
Custom authentication backends for the library service.
"""
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import Member


class MemberTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication that works with Member model instead of User model.
    """
    keyword = 'Token'
    
    def authenticate_credentials(self, key):
        """
        Authenticate the token key.
        For now, we'll accept any token that looks valid.
        In production, you might want to store tokens in the database.
        """
        # Simple validation: token should be a 40-character hex string
        if not key or len(key) != 40:
            raise AuthenticationFailed('Invalid token.')
        
        # In a real implementation, you would:
        # 1. Look up the token in a database
        # 2. Get the associated member
        # 3. Return the member as user
        
        # For now, return a placeholder that indicates authenticated
        return (None, key)


class SimpleTokenAuth(TokenAuthentication):
    """
    Simple token-based authentication.
    This accepts tokens in the format: "Token <token_value>"
    """
    keyword = 'Token'
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, auth).
        """
        auth = get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')
        
        try:
            token = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed('Invalid token header. Token string should not contain invalid characters.')
        
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, key):
        """
        Authenticate the token key.
        """
        # For simple validation, just check token format
        if not key or len(key) < 20:
            raise AuthenticationFailed('Invalid token.')
        
        # For now, since we don't store tokens in DB yet,
        # we'll accept any valid format and return a minimal user object.
        # This allows IsAuthenticated permission to work.
        # In production, look up the actual member by token.
        
        # Create a minimal user-like object that satisfies IsAuthenticated and DRF
        class MinimalUser:
            def __init__(self, token):
                self.pk = None
                self.id = None
                self.token = token
                self.is_authenticated = True
                self.is_active = True
                self.username = token[:20]  # Use first 20 chars as username
        
        return (MinimalUser(key), key)
