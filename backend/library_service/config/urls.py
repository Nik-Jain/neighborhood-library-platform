"""
URL Configuration for Library Service project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from library_service.apps.core.auth_views import SignupView, LoginView, LogoutView, CurrentUserView

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint for container orchestration."""
    return Response({'status': 'healthy'})

urlpatterns = [
    # Health check
    path('api/health/', health_check, name='health-check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication endpoints
    path('api/v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('api/v1/auth/login/', LoginView.as_view(), name='login'),
    path('api/v1/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/v1/auth/user/', CurrentUserView.as_view(), name='current-user'),
    
    # Legacy token auth endpoint for backward compatibility
    path('api-token-auth/', LoginView.as_view(), name='api-token-auth'),
    
    # API endpoints
    path('api/v1/', include('library_service.apps.core.urls')),
]
