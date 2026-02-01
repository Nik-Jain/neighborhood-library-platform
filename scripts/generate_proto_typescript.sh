#!/bin/bash
# Script to generate TypeScript protobuf code from .proto files

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Generating TypeScript Protocol Buffer code...${NC}"

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define paths
PROTO_DIR="$PROJECT_ROOT/proto"
OUTPUT_DIR="$PROJECT_ROOT/frontend/src/proto"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo -e "${RED}Error: protoc (Protocol Buffer Compiler) is not installed${NC}"
    echo "Please install it first:"
    echo "  Ubuntu/Debian: sudo apt-get install protobuf-compiler"
    echo "  macOS: brew install protobuf"
    exit 1
fi

# Check if protoc-gen-ts is available
if ! command -v protoc-gen-ts &> /dev/null; then
    echo -e "${YELLOW}Installing protoc-gen-ts plugin...${NC}"
    cd "$PROJECT_ROOT/frontend"
    npm install --save-dev ts-proto
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install ts-proto${NC}"
        exit 1
    fi
fi

# Generate TypeScript code from proto files
echo "Generating from: $PROTO_DIR"
echo "Output to: $OUTPUT_DIR"

cd "$PROJECT_ROOT"

# Use ts-proto for generation (better TypeScript support)
npx protoc \
    --plugin="$PROJECT_ROOT/frontend/node_modules/.bin/protoc-gen-ts_proto" \
    --ts_proto_out="$OUTPUT_DIR" \
    --ts_proto_opt=outputServices=false \
    --ts_proto_opt=outputClientImpl=false \
    --ts_proto_opt=esModuleInterop=true \
    --proto_path="$PROTO_DIR" \
    "$PROTO_DIR/library.proto"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully generated TypeScript protobuf code${NC}"
    echo "Generated files:"
    ls -lh "$OUTPUT_DIR"
else
    echo -e "${RED}✗ Failed to generate TypeScript protobuf code${NC}"
    exit 1
fi

echo -e "${GREEN}Done!${NC}"
