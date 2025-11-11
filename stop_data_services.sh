#!/bin/bash

# Stop Data Services

echo "🛑 Stopping Data Services..."
echo "======================================"
echo ""

# Stop services
docker-compose -f docker-compose.data-services.yml down

echo ""
echo "✅ Data Services stopped successfully!"
echo ""
echo "Note: Key storage volume is preserved."
echo "To remove volumes, run:"
echo "  docker-compose -f docker-compose.data-services.yml down -v"
echo ""

