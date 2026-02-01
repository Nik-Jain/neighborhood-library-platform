#!/bin/bash
# Script to compile Protocol Buffer definitions to Python and TypeScript

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Compiling Protocol Buffers...${NC}"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$PROJECT_ROOT/proto"
BACKEND_OUT_DIR="$PROJECT_ROOT/backend/library_service/apps/core/proto_generated"
FRONTEND_OUT_DIR="$PROJECT_ROOT/frontend/src/lib/proto_generated"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}Proto directory: $PROTO_DIR${NC}"

# Create output directories if they don't exist
mkdir -p "$BACKEND_OUT_DIR"
mkdir -p "$FRONTEND_OUT_DIR"

# Compile Python protobuf files
echo -e "${BLUE}Compiling Python protobuf files...${NC}"
python -m grpc_tools.protoc \
    --proto_path="$PROTO_DIR" \
    --python_out="$BACKEND_OUT_DIR" \
    --grpc_python_out="$BACKEND_OUT_DIR" \
    "$PROTO_DIR/library.proto"

# Create __init__.py for Python package
echo "# Generated protobuf files" > "$BACKEND_OUT_DIR/__init__.py"

echo -e "${GREEN}✓ Python protobuf files generated successfully${NC}"

# Compile TypeScript/JavaScript protobuf files
echo -e "${BLUE}Compiling TypeScript/JavaScript protobuf files...${NC}"

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo "Warning: protoc not found. Skipping TypeScript generation."
    echo "Install protoc to generate TypeScript files: https://grpc.io/docs/protoc-installation/"
else
    # Check if protoc-gen-ts is available
    if command -v protoc-gen-ts &> /dev/null || [ -f "$PROJECT_ROOT/frontend/node_modules/.bin/protoc-gen-ts" ]; then
        # Generate TypeScript files
        protoc \
            --proto_path="$PROTO_DIR" \
            --plugin="protoc-gen-ts=$PROJECT_ROOT/frontend/node_modules/.bin/protoc-gen-ts" \
            --js_out="import_style=commonjs,binary:$FRONTEND_OUT_DIR" \
            --ts_out="$FRONTEND_OUT_DIR" \
            "$PROTO_DIR/library.proto"
        
        echo -e "${GREEN}✓ TypeScript protobuf files generated successfully${NC}"
    else
        echo "Warning: protoc-gen-ts not found. Generating JavaScript files only."
        protoc \
            --proto_path="$PROTO_DIR" \
            --js_out="import_style=commonjs,binary:$FRONTEND_OUT_DIR" \
            "$PROTO_DIR/library.proto"
        
        echo -e "${GREEN}✓ JavaScript protobuf files generated${NC}"
    fi
fi

echo -e "${GREEN}✓ Protocol Buffer compilation complete!${NC}"
