"""
Custom exception handlers for the core library service application.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats error responses consistently.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': True,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'status_code': response.status_code,
            'details': response.data
        }
    else:
        # Log unexpected errors
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        
        response = Response(
            {
                'error': True,
                'message': 'An unexpected error occurred.',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
