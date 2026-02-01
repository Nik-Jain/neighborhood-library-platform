"""
Token model for API authentication.
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import secrets


class APIToken(models.Model):
    """
    Token-based authentication for API access.
    Links a token to a Django User (which in turn links to a Member).
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_tokens'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'

    def __str__(self):
        return f'Token for {self.user.username}'

    @classmethod
    def generate_key(cls):
        """Generate a secure random token key."""
        return secrets.token_hex(20)

    def save(self, *args, **kwargs):
        """Generate token key if not set."""
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)
