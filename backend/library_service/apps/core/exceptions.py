"""
Custom exceptions and exception handlers for the library service application.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exception Classes
# ============================================================================

class LibraryServiceException(APIException):
    """Base exception for library service errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A library service error occurred.'
    default_code = 'library_service_error'


class ResourceNotFoundException(LibraryServiceException):
    """Base exception for resource not found errors."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'resource_not_found'


class MemberNotFoundException(ResourceNotFoundException):
    """Raised when member is not found."""
    default_detail = 'Member not found.'
    default_code = 'member_not_found'


class BookNotFoundException(ResourceNotFoundException):
    """Raised when book is not found."""
    default_detail = 'Book not found.'
    default_code = 'book_not_found'


class BorrowingNotFoundException(ResourceNotFoundException):
    """Raised when borrowing record is not found."""
    default_detail = 'Borrowing not found.'
    default_code = 'borrowing_not_found'


class MemberNotActiveException(LibraryServiceException):
    """Raised when attempting operations with inactive member."""
    default_detail = 'Member account is not active.'
    default_code = 'member_not_active'


class MemberHasActiveBorrowingsException(LibraryServiceException):
    """Raised when attempting to delete member with active borrowings."""
    default_detail = 'Cannot delete member with active borrowings.'
    default_code = 'member_has_active_borrowings'


class BookNotAvailableException(LibraryServiceException):
    """Raised when book has no available copies."""
    default_detail = 'Book is not available for borrowing.'
    default_code = 'book_not_available'


class BookAlreadyBorrowedException(LibraryServiceException):
    """Raised when member already has the same book borrowed."""
    default_detail = 'Member already has this book borrowed.'
    default_code = 'book_already_borrowed'


class BookHasActiveBorrowingsException(LibraryServiceException):
    """Raised when attempting to delete book with active borrowings."""
    default_detail = 'Cannot delete book with active borrowings.'
    default_code = 'book_has_active_borrowings'


class BorrowingAlreadyReturnedException(LibraryServiceException):
    """Raised when attempting to return already returned book."""
    default_detail = 'This book has already been returned.'
    default_code = 'borrowing_already_returned'


class ConcurrencyException(LibraryServiceException):
    """Raised when concurrent operation causes conflict."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Operation failed due to concurrent modification. Please retry.'
    default_code = 'concurrency_conflict'


class InsufficientCopiesException(LibraryServiceException):
    """Raised when available copies would become negative."""
    default_detail = 'Insufficient available copies for this operation.'
    default_code = 'insufficient_copies'


class InvalidBookCopiesException(LibraryServiceException):
    """Raised when book copies validation fails."""
    default_detail = 'Available copies cannot exceed total copies.'
    default_code = 'invalid_book_copies'


# ============================================================================
# Exception Handler
# ============================================================================

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
