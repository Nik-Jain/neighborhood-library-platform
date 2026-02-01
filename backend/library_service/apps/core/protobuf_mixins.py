"""
Mixin to add Protocol Buffer support to Django REST Framework ViewSets.
"""
from .proto_generated import library_pb2


class ProtobufSupportMixin:
    """
    Mixin to add protobuf message class to viewset responses.
    This enables automatic protobuf serialization when client requests it via Accept header.
    """
    protobuf_message_class = None
    protobuf_list_message_class = None
    
    def finalize_response(self, request, response, *args, **kwargs):
        """
        Attach the appropriate protobuf message class based on the action.
        """
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Determine which protobuf message class to use
        if self.action == 'list':
            # List action - use the list message class
            message_class = self.protobuf_list_message_class
        else:
            # Single object actions (retrieve, create, update, etc.)
            message_class = self.protobuf_message_class
        
        # Attach to response so renderer can use it
        if message_class:
            response.protobuf_message_class = message_class
        
        return response


class MemberProtobufMixin(ProtobufSupportMixin):
    """Protobuf support for Member ViewSet."""
    protobuf_message_class = library_pb2.Member
    protobuf_list_message_class = library_pb2.MemberList


class BookProtobufMixin(ProtobufSupportMixin):
    """Protobuf support for Book ViewSet."""
    protobuf_message_class = library_pb2.Book
    protobuf_list_message_class = library_pb2.BookList


class BorrowingProtobufMixin(ProtobufSupportMixin):
    """Protobuf support for Borrowing ViewSet."""
    protobuf_message_class = library_pb2.Borrowing
    protobuf_list_message_class = library_pb2.BorrowingList


class FineProtobufMixin(ProtobufSupportMixin):
    """Protobuf support for Fine ViewSet."""
    protobuf_message_class = library_pb2.Fine
    protobuf_list_message_class = library_pb2.FineList


class AuthProtobufMixin:
    """
    Mixin for APIView-based auth endpoints to support protobuf.
    This is simpler than viewset mixin since APIViews don't have actions.
    """
    protobuf_request_class = None
    protobuf_response_class = None
    
    def finalize_response(self, request, response, *args, **kwargs):
        """Attach protobuf message classes for auth responses."""
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # For auth endpoints, always use the response class
        if self.protobuf_response_class:
            response.protobuf_message_class = self.protobuf_response_class
        
        return response


class LoginProtobufMixin(AuthProtobufMixin):
    """Protobuf support for Login endpoint."""
    protobuf_request_class = library_pb2.LoginRequest
    protobuf_response_class = library_pb2.LoginResponse


class SignupProtobufMixin(AuthProtobufMixin):
    """Protobuf support for Signup endpoint."""
    protobuf_request_class = library_pb2.SignupRequest
    protobuf_response_class = library_pb2.SignupResponse
