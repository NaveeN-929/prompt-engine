#!/bin/bash
set -e

# Build script for Validation LLM Service Docker image

echo "🐳 Building Validation LLM Service Docker Image"
echo "================================================"

# Configuration
IMAGE_NAME="paytechneodemo/validator"
TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

# Build context
BUILD_CONTEXT="."
DOCKERFILE="Dockerfile"

echo "📋 Build Configuration:"
echo "   Image Name: ${FULL_IMAGE_NAME}"
echo "   Build Context: ${BUILD_CONTEXT}"
echo "   Dockerfile: ${DOCKERFILE}"
echo ""

# Check if Dockerfile exists
if [ ! -f "${DOCKERFILE}" ]; then
    echo "❌ Error: Dockerfile not found at ${DOCKERFILE}"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Build the image
echo "🔨 Building Docker image..."
docker build \
    --tag "${FULL_IMAGE_NAME}" \
    --file "${DOCKERFILE}" \
    --progress=plain \
    "${BUILD_CONTEXT}"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build completed successfully!"
    echo "   Image: ${FULL_IMAGE_NAME}"
    
    # Show image size
    echo ""
    echo "📊 Image Information:"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Test the image:"
    echo "      docker run --rm -p 5002:5002 ${FULL_IMAGE_NAME}"
    echo ""
    echo "   2. Push to registry:"
    echo "      docker push ${FULL_IMAGE_NAME}"
    echo ""
    echo "   3. Deploy with docker-compose:"
    echo "      docker-compose -f ../docker-compose.paytechneodemo.yml up -d validator"
    echo ""
    
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi
