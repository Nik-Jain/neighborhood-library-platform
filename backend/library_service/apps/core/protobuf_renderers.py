"""
Protocol Buffer renderers and parsers for Django REST Framework.
Allows REST API to use protobuf serialization instead of JSON.
"""
from rest_framework import renderers, parsers
from rest_framework.exceptions import ParseError
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import DecodeError
import importlib


class ProtobufRenderer(renderers.BaseRenderer):
    """
    Renderer that serializes responses to Protocol Buffer binary format.
    
    Usage:
        Add to DEFAULT_RENDERER_CLASSES in settings.py
        or specify in view: renderer_classes = [ProtobufRenderer, JSONRenderer]
    """
    media_type = 'application/x-protobuf'
    format = 'protobuf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render data to protobuf binary format.
        
        Expects the view to set protobuf_message_class on the response.
        """
        if data is None:
            return b''
        
        # Get the protobuf message class from renderer context
        response = renderer_context.get('response') if renderer_context else None
        message_class = getattr(response, 'protobuf_message_class', None) if response else None
        
        if message_class is None:
            # Fallback to JSON-like rendering if no protobuf class specified
            return str(data).encode('utf-8')
        
        try:
            # Convert dict to protobuf message
            message = self._dict_to_protobuf(data, message_class)
            return message.SerializeToString()
        except Exception as e:
            # Fallback to string representation on error
            return str(data).encode('utf-8')
    
    def _dict_to_protobuf(self, data, message_class):
        """Convert Python dict to protobuf message."""
        message = message_class()
        
        # Handle paginated responses
        if isinstance(data, dict) and 'results' in data:
            # Paginated list response
            if hasattr(message, 'results'):
                for item in data.get('results', []):
                    result_message = message.results.add()
                    self._populate_message(result_message, item)
                
                if 'count' in data:
                    message.count = data['count']
                if 'next' in data and data['next']:
                    message.next = str(data['next'])
                if 'previous' in data and data['previous']:
                    message.previous = str(data['previous'])
            return message
        elif isinstance(data, list):
            # Plain list (shouldn't happen with pagination, but handle it)
            return message
        else:
            # Single object
            self._populate_message(message, data)
            return message
    
    def _populate_message(self, message, data):
        """Populate a protobuf message with data from dict."""
        if not isinstance(data, dict):
            return
        
        for key, value in data.items():
            if value is None:
                continue
            
            # Convert field names (e.g., snake_case to camelCase if needed)
            field_name = key
            
            if hasattr(message, field_name):
                # Get the field descriptor
                field = message.DESCRIPTOR.fields_by_name.get(field_name)
                if field is None:
                    continue
                
                try:
                    # Handle different field types
                    if isinstance(value, (int, float, bool, str)):
                        setattr(message, field_name, value)
                    elif isinstance(value, dict):
                        # Nested message
                        nested_message = getattr(message, field_name)
                        self._populate_message(nested_message, value)
                    elif isinstance(value, list):
                        # Repeated field
                        repeated_field = getattr(message, field_name)
                        for item in value:
                            if isinstance(item, dict):
                                nested = repeated_field.add()
                                self._populate_message(nested, item)
                            else:
                                repeated_field.append(item)
                except Exception:
                    # Skip fields that can't be set
                    pass


class ProtobufParser(parsers.BaseParser):
    """
    Parser that deserializes Protocol Buffer binary format to Python dict.
    
    Usage:
        Add to DEFAULT_PARSER_CLASSES in settings.py
        or specify in view: parser_classes = [ProtobufParser, JSONParser]
    """
    media_type = 'application/x-protobuf'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parse incoming protobuf binary data to Python dict.
        
        Expects the view to set protobuf_request_class or protobuf_message_class attribute.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Get the protobuf message class from view
            view = parser_context.get('view') if parser_context else None
            request = parser_context.get('request') if parser_context else None
            
            logger.info(f"ProtobufParser.parse() called for {request.path if request else 'unknown'}")
            logger.info(f"Media type: {media_type}")
            
            # Try protobuf_request_class first (for auth endpoints)
            message_class = getattr(view, 'protobuf_request_class', None) if view else None
            
            # Fall back to protobuf_message_class (for data endpoints)
            if message_class is None:
                message_class = getattr(view, 'protobuf_message_class', None) if view else None
            
            # Try to infer from URL path
            if message_class is None and request:
                message_class = self._infer_message_class(request.path)
                logger.info(f"Inferred message class from URL: {message_class}")
            
            if message_class is None:
                logger.error(f"Could not determine message class for {request.path if request else 'unknown'}")
                raise ParseError('Protobuf message class not specified for this endpoint')
            
            # Read the binary data
            data = stream.read()
            logger.info(f"Received {len(data)} bytes of data")
            logger.info(f"First 20 bytes (hex): {data[:20].hex()}")
            
            # Check if data looks like JSON (for better error messages)
            if data.startswith(b'{') or data.startswith(b'['):
                logger.error("Received JSON data instead of protobuf!")
                raise ParseError(
                    'Received JSON data but expected protobuf. '
                    'This usually means protobuf encoding failed on the client side. '
                    'Make sure Content-Type and data format match. '
                    'Consider using JSON instead (Accept: application/json).'
                )
            
            if not data:
                logger.error("Empty request body")
                raise ParseError('Empty request body')
            
            # Parse protobuf message
            message = message_class()
            try:
                message.ParseFromString(data)
                logger.info(f"Successfully parsed {message_class.__name__}")
            except Exception as e:
                logger.error(f"Failed to parse protobuf: {str(e)}")
                raise ParseError(
                    f'Invalid protobuf data: {str(e)}. '
                    f'Expected {message_class.__name__} message.'
                )
            
            # Convert to dict using correct MessageToDict parameters
            return MessageToDict(
                message,
                preserving_proto_field_name=True,
                always_print_fields_with_no_presence=False
            )
        except DecodeError as e:
            logger.error(f"DecodeError: {str(e)}")
            raise ParseError(f'Invalid protobuf data: {str(e)}')
        except ParseError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ProtobufParser: {str(e)}")
            raise ParseError(f'Error parsing protobuf: {str(e)}')
    
    def _infer_message_class(self, path):
        """Infer protobuf message class from URL path."""
        if '/auth/login/' in path:
            return library_pb2.LoginRequest
        elif '/auth/signup/' in path:
            return library_pb2.SignupRequest
        elif '/members/' in path:
            return library_pb2.Member
        elif '/books/' in path:
            return library_pb2.Book
        elif '/borrowings/' in path:
            return library_pb2.Borrowing
        elif '/fines/' in path:
            return library_pb2.Fine
        return None



class ProtobufJSONRenderer(renderers.JSONRenderer):
    """
    Hybrid renderer that can convert protobuf-aware data to JSON.
    Useful for supporting both protobuf and JSON in the same view.
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render as JSON, handling any protobuf-specific formatting."""
        # Use standard JSON rendering
        return super().render(data, accepted_media_type, renderer_context)
