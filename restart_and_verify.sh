#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Restart Services & Verify Quality Improvement               ║"
echo "║  This will load the updated code with quality improvements    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Stop services
echo -e "${BLUE}Step 1: Stopping all services...${NC}"
./stop_all_services.sh > /dev/null 2>&1
sleep 5

# Verify stopped
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Prompt Engine still running, force stopping...${NC}"
    pkill -f "python3 -m app.main" 2>/dev/null
    sleep 2
fi

if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Autonomous Agent still running, force stopping...${NC}"
    pkill -f "python3 server_final.py" 2>/dev/null
    sleep 2
fi

echo -e "${GREEN}✓ Services stopped${NC}"
echo ""

# Step 2: Clear Python cache
echo -e "${BLUE}Step 2: Clearing Python cache...${NC}"
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo -e "${GREEN}✓ Cache cleared${NC}"
echo ""

# Step 3: Start services
echo -e "${BLUE}Step 3: Starting services with updated code...${NC}"
echo "  This will take about 30-45 seconds..."
echo ""

# Start in background and capture output
./start_all_services.sh > /tmp/service_start.log 2>&1 &
START_PID=$!

# Wait with progress indicator
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Step 4: Verify services are up
echo -e "${BLUE}Step 4: Verifying services...${NC}"

# Check Prompt Engine
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Prompt Engine running${NC}"
    
    # Check for quality improvement in logs
    if grep -q "Quality Improvement Engine enabled" /tmp/service_start.log 2>/dev/null; then
        echo -e "${GREEN}✓ Quality Improvement Engine loaded!${NC}"
    else
        echo -e "${YELLOW}⚠ Could not verify Quality Improvement Engine in logs${NC}"
        echo "  Check logs manually if verification fails"
    fi
else
    echo -e "${RED}✗ Prompt Engine not responding${NC}"
    echo "  Check logs/prompt_engine.log for errors"
    exit 1
fi

# Check Autonomous Agent
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Autonomous Agent running${NC}"
else
    echo -e "${RED}✗ Autonomous Agent not responding${NC}"
    echo "  Check logs/autonomous_agent.log for errors"
    exit 1
fi

echo ""

# Step 5: Run verification
echo -e "${BLUE}Step 5: Running quality improvement verification...${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

./verify_quality_improvement.sh

# Capture exit code
VERIFY_RESULT=$?

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ $VERIFY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ VERIFICATION SUCCESSFUL!${NC}"
    echo ""
    echo "Quality improvement is working correctly."
    echo "The system learned from the first run and improved on the second."
else
    echo -e "${YELLOW}⚠ VERIFICATION NEEDS ATTENTION${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Check if 'Quality Improvement Engine enabled' appears in logs"
    echo "2. Try running verification again: ./verify_quality_improvement.sh"
    echo "3. Check logs/prompt_engine.log and logs/autonomous_agent.log"
    echo ""
    echo "If score is still not improving, there may be an issue with"
    echo "the integration. Check for error messages in the logs."
fi

echo ""
exit $VERIFY_RESULT

