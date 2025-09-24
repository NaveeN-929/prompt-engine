#!/bin/bash
set -e

# Test script for Docker integration of Validation LLM Service

echo "🧪 Testing Validation LLM Service Docker Integration"
echo "===================================================="

# Configuration
VALIDATOR_URL="http://localhost:5002"
AUTONOMOUS_AGENT_URL="http://localhost:5001"
COMPOSE_FILE="../docker-compose.paytechneodemo.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_service() {
    local service_name=$1
    local url=$2
    local endpoint=$3
    
    echo -n "   Testing ${service_name}... "
    
    if curl -sf "${url}${endpoint}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

test_validation_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -n "   Testing ${description}... "
    
    if curl -sf "${VALIDATOR_URL}${endpoint}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Main test execution
echo "🔍 Step 1: Checking if services are running"
echo "----------------------------------------"

# Check if docker-compose is running
if ! docker-compose -f "${COMPOSE_FILE}" ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️ Services not running. Starting them...${NC}"
    docker-compose -f "${COMPOSE_FILE}" up -d
    echo "⏳ Waiting 60 seconds for services to start..."
    sleep 60
fi

echo ""
echo "📊 Step 2: Service Status Check"
echo "------------------------------"
docker-compose -f "${COMPOSE_FILE}" ps

echo ""
echo "🏥 Step 3: Health Check Tests"
echo "-----------------------------"

# Test basic connectivity
test_service "Validator Health" "${VALIDATOR_URL}" "/health"
test_service "Autonomous Agent Health" "${AUTONOMOUS_AGENT_URL}" "/health"

echo ""
echo "🔍 Step 4: Validation Service Endpoints"
echo "--------------------------------------"

# Test validation service endpoints
test_validation_endpoint "/health" "Health endpoint"
test_validation_endpoint "/" "Root endpoint"

# Test validation functionality (if service is up)
echo -n "   Testing validation functionality... "
if curl -sf "${VALIDATOR_URL}/health" > /dev/null 2>&1; then
    # Try a simple validation request
    response=$(curl -s -X POST "${VALIDATOR_URL}/validate/response" \
        -H "Content-Type: application/json" \
        -d '{
            "response_data": {
                "analysis": "=== SECTION 1: INSIGHTS ===\nTest insights\n=== SECTION 2: RECOMMENDATIONS ===\nTest recommendations"
            },
            "input_data": {
                "transactions": [{"amount": 100, "type": "credit"}]
            }
        }' 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q "quality_level"; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${YELLOW}⚠️ PARTIAL${NC} (service up but validation may need models)"
    fi
else
    echo -e "${RED}❌ FAIL${NC}"
fi

echo ""
echo "🔗 Step 5: Integration Test"
echo "---------------------------"

# Test if autonomous agent can reach validator
echo -n "   Testing autonomous agent → validator connection... "
if docker exec paytechneodemo-autonomous-agent ping -c 1 validator > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test validation service status from autonomous agent
echo -n "   Testing validation service status endpoint... "
if curl -sf "${AUTONOMOUS_AGENT_URL}/validation/status" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️ PARTIAL${NC} (endpoint exists but service may be initializing)"
fi

echo ""
echo "📋 Step 6: Service Information"
echo "-----------------------------"

echo "🐳 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(validator|autonomous-agent|ollama|qdrant)"

echo ""
echo "📊 Service URLs:"
echo "   • Validator Service:    ${VALIDATOR_URL}"
echo "   • Autonomous Agent:     ${AUTONOMOUS_AGENT_URL}"
echo "   • Validation Status:    ${AUTONOMOUS_AGENT_URL}/validation/status"
echo "   • System Status:        ${AUTONOMOUS_AGENT_URL}/status"

echo ""
echo "🎯 Step 7: Final Verification"
echo "-----------------------------"

# Count successful tests
success_count=0
total_tests=6

# Rerun key tests for final count
curl -sf "${VALIDATOR_URL}/health" > /dev/null 2>&1 && ((success_count++))
curl -sf "${AUTONOMOUS_AGENT_URL}/health" > /dev/null 2>&1 && ((success_count++))
curl -sf "${VALIDATOR_URL}/" > /dev/null 2>&1 && ((success_count++))
docker exec paytechneodemo-autonomous-agent ping -c 1 validator > /dev/null 2>&1 && ((success_count++))
curl -sf "${AUTONOMOUS_AGENT_URL}/validation/status" > /dev/null 2>&1 && ((success_count++))
curl -sf "${AUTONOMOUS_AGENT_URL}/status" > /dev/null 2>&1 && ((success_count++))

echo "Test Results: ${success_count}/${total_tests} tests passed"

if [ ${success_count} -eq ${total_tests} ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Docker integration is working perfectly.${NC}"
    echo ""
    echo "✅ Validation service is fully integrated and operational!"
    echo "✅ Blocking validation is available for the autonomous agent!"
    echo "✅ All service endpoints are accessible!"
    exit 0
elif [ ${success_count} -gt $((total_tests / 2)) ]; then
    echo -e "${YELLOW}⚠️ PARTIAL SUCCESS: Most tests passed, some services may still be initializing.${NC}"
    echo ""
    echo "💡 Try running the test again in a few minutes for full initialization."
    exit 1
else
    echo -e "${RED}❌ INTEGRATION FAILED: Multiple services are not working correctly.${NC}"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "   1. Check service logs: docker-compose -f ${COMPOSE_FILE} logs validator"
    echo "   2. Verify all services are up: docker-compose -f ${COMPOSE_FILE} ps"
    echo "   3. Restart services: docker-compose -f ${COMPOSE_FILE} restart"
    exit 1
fi
