#!/bin/bash
# Script to generate Python protobuf code from .proto files

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Generating Python Protocol Buffer code...${NC}"

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define paths
PROTO_DIR="$PROJECT_ROOT/proto"
OUTPUT_DIR="$PROJECT_ROOT/backend/library_service/apps/core/proto_generated"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Create __init__.py to make it a Python package
touch "$OUTPUT_DIR/__init__.py"

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo -e "${RED}Error: protoc (Protocol Buffer Compiler) is not installed${NC}"
    echo "Please install it first:"
    echo "  Ubuntu/Debian: sudo apt-get install protobuf-compiler"
    echo "  macOS: brew install protobuf"
    echo "  Or download from: https://github.com/protocolbuffers/protobuf/releases"
    exit 1
fi

# Generate Python code from proto files
echo "Generating from: $PROTO_DIR"
echo "Output to: $OUTPUT_DIR"

cd "$PROJECT_ROOT"

python -m grpc_tools.protoc \
    --proto_path="$PROTO_DIR" \
    --python_out="$OUTPUT_DIR" \
    --grpc_python_out="$OUTPUT_DIR" \
    "$PROTO_DIR/library.proto"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully generated Python protobuf code${NC}"
    echo "Generated files:"
    ls -lh "$OUTPUT_DIR"
else
    echo -e "${RED}✗ Failed to generate Python protobuf code${NC}"
    exit 1
fi

# Fix import statements in generated files (if needed)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' 's/^import library_pb2/from . import library_pb2/' "$OUTPUT_DIR/library_pb2_grpc.py" 2>/dev/null || true
else
    # Linux
    sed -i 's/^import library_pb2/from . import library_pb2/' "$OUTPUT_DIR/library_pb2_grpc.py" 2>/dev/null || true
fi

echo -e "${GREEN}Done!${NC}"
