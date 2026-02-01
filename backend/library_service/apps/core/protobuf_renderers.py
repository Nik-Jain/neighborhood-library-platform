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
        
        Expects the view to set protobuf_message_class attribute.
        """
        try:
            # Get the protobuf message class from view
            view = parser_context.get('view') if parser_context else None
            message_class = getattr(view, 'protobuf_message_class', None) if view else None
            
            if message_class is None:
                raise ParseError('Protobuf message class not specified')
            
            # Read the binary data
            data = stream.read()
            
            # Parse protobuf message
            message = message_class()
            message.ParseFromString(data)
            
            # Convert to dict
            return MessageToDict(
                message,
                preserving_proto_field_name=True,
                including_default_value_fields=False
            )
        except DecodeError as e:
            raise ParseError(f'Invalid protobuf data: {str(e)}')
        except Exception as e:
            raise ParseError(f'Error parsing protobuf: {str(e)}')


class ProtobufJSONRenderer(renderers.JSONRenderer):
    """
    Hybrid renderer that can convert protobuf-aware data to JSON.
    Useful for supporting both protobuf and JSON in the same view.
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render as JSON, handling any protobuf-specific formatting."""
        # Use standard JSON rendering
        return super().render(data, accepted_media_type, renderer_context)
