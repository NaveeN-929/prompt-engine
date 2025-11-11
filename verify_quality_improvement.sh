#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Quality Improvement Verification Script                      ║"
echo "║  Tests that validation scores IMPROVE for repeated datasets   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if services are running
echo -e "${BLUE}Step 1: Checking if services are running...${NC}"
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Prompt Engine not running${NC}"
    echo "  Please start services: ./start_all_services.sh"
    exit 1
fi

if ! curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Autonomous Agent not running${NC}"
    echo "  Please start services: ./start_all_services.sh"
    exit 1
fi

echo -e "${GREEN}✓ Services are running${NC}"
echo ""

# Check for test data
echo -e "${BLUE}Step 2: Checking for test data...${NC}"
TEST_DATA="data/generated_data/dataset_0001.json"

if [ ! -f "$TEST_DATA" ]; then
    echo -e "${YELLOW}⚠ Test data not found, generating...${NC}"
    cd data && python3 data-script.py --quick 1 && cd ..
fi

if [ -f "$TEST_DATA" ]; then
    echo -e "${GREEN}✓ Test data available${NC}"
else
    echo -e "${RED}✗ Could not find test data${NC}"
    exit 1
fi

echo ""

# Run first analysis
echo -e "${BLUE}Step 3: Running FIRST analysis (learning phase)...${NC}"
echo "  This will establish a baseline score"
echo ""

# Wrap the dataset in input_data field as required by the API
WRAPPED_DATA=$(cat "$TEST_DATA" | python3 -c "import sys, json; data = json.load(sys.stdin); print(json.dumps({'input_data': data}))")

RESPONSE1=$(curl -s -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d "$WRAPPED_DATA")

# Extract scores (basic parsing)
SCORE1=$(echo "$RESPONSE1" | grep -o '"overall_score":[^,}]*' | head -1 | cut -d':' -f2 | tr -d ' ')

if [ -z "$SCORE1" ]; then
    echo -e "${YELLOW}⚠ Could not extract validation score from response${NC}"
    echo "  Response preview:"
    echo "$RESPONSE1" | head -c 500
    echo ""
    SCORE1="N/A"
else
    echo -e "${GREEN}✓ First run complete${NC}"
    echo -e "  Validation score: ${YELLOW}${SCORE1}${NC}"
fi

echo ""
echo -e "${BLUE}Waiting 3 seconds for learning to complete...${NC}"
sleep 3
echo ""

# Run second analysis
echo -e "${BLUE}Step 4: Running SECOND analysis (improvement phase)...${NC}"
echo "  This should use improved prompt and get higher score"
echo ""

# Use the same wrapped data
RESPONSE2=$(curl -s -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d "$WRAPPED_DATA")

# Extract scores
SCORE2=$(echo "$RESPONSE2" | grep -o '"overall_score":[^,}]*' | head -1 | cut -d':' -f2 | tr -d ' ')

if [ -z "$SCORE2" ]; then
    echo -e "${YELLOW}⚠ Could not extract validation score from response${NC}"
    echo "  Response preview:"
    echo "$RESPONSE2" | head -c 500
    echo ""
    SCORE2="N/A"
else
    echo -e "${GREEN}✓ Second run complete${NC}"
    echo -e "  Validation score: ${YELLOW}${SCORE2}${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                        RESULTS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  First Run:  ${SCORE1}"
echo "  Second Run: ${SCORE2}"
echo ""

# Compare scores (if numeric)
if [[ "$SCORE1" =~ ^[0-9.]+$ ]] && [[ "$SCORE2" =~ ^[0-9.]+$ ]]; then
    IMPROVED=$(echo "$SCORE2 > $SCORE1" | bc -l)
    DIFF=$(echo "$SCORE2 - $SCORE1" | bc -l)
    PERCENT=$(echo "scale=1; ($DIFF / $SCORE1) * 100" | bc -l)
    
    if [ "$IMPROVED" -eq 1 ]; then
        echo -e "${GREEN}✓ SUCCESS: Score IMPROVED by ${DIFF} (+${PERCENT}%)${NC}"
        echo ""
        echo "  Quality improvement is WORKING! 🎉"
        echo "  The system learned from the first run and generated"
        echo "  a better prompt for the second run."
        echo ""
        exit 0
    else
        echo -e "${RED}✗ ISSUE: Score did NOT improve${NC}"
        echo ""
        echo "  Possible causes:"
        echo "  1. System may need more time to learn (try again)"
        echo "  2. Quality engine may not be initialized"
        echo "  3. Check logs for errors"
        echo ""
        echo "  Check Prompt Engine logs for:"
        echo "  - '🧠 Quality Improvement Engine enabled'"
        echo "  - '🎯 Using quality-improved prompt'"
        echo ""
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Could not compare scores (non-numeric)${NC}"
    echo ""
    echo "  Please check the full responses manually"
    echo "  Look for validation_result.overall_score in the JSON"
    echo ""
    exit 1
fi

