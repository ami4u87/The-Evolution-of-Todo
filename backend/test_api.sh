#!/bin/bash
# API Testing Script for Todo Backend
# This script demonstrates how to test all API endpoints

set -e  # Exit on error

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Todo API Test Script - Phase II${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${GREEN}Test 1: Health Check${NC}"
echo "GET $BASE_URL/"
curl -s $BASE_URL/ | jq .
echo ""

# Test 2: Health endpoint
echo -e "${GREEN}Test 2: Health Endpoint${NC}"
echo "GET $BASE_URL/health"
curl -s $BASE_URL/health | jq .
echo ""

# Note: The following tests require a valid JWT token
echo -e "${RED}========================================${NC}"
echo -e "${RED}AUTHENTICATION REQUIRED${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo "To test authenticated endpoints, you need a JWT token from Better Auth."
echo "Set the TOKEN environment variable:"
echo ""
echo "  export TOKEN='your_jwt_token_here'"
echo ""

# Check if TOKEN is set
if [ -z "$TOKEN" ]; then
    echo -e "${RED}ERROR: TOKEN environment variable not set${NC}"
    echo "Skipping authenticated endpoint tests."
    echo ""
    echo "To get a token, you need to:"
    echo "1. Run the frontend (Better Auth)"
    echo "2. Sign up / Log in"
    echo "3. Extract the JWT token from the frontend"
    echo "4. Set it as environment variable: export TOKEN='...'"
    exit 0
fi

echo -e "${GREEN}Token found! Testing authenticated endpoints...${NC}"
echo ""

# Test 3: List Tasks (should be empty initially)
echo -e "${GREEN}Test 3: List Tasks (Empty)${NC}"
echo "GET $API_URL/tasks"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks | jq .
echo ""

# Test 4: Create Task
echo -e "${GREEN}Test 4: Create Task${NC}"
echo "POST $API_URL/tasks"
TASK_RESPONSE=$(curl -s -X POST $API_URL/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }')

echo "$TASK_RESPONSE" | jq .

# Extract task ID from response
TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')
echo ""
echo "Created task ID: $TASK_ID"
echo ""

# Test 5: Get Task by ID
echo -e "${GREEN}Test 5: Get Task by ID${NC}"
echo "GET $API_URL/tasks/$TASK_ID"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks/$TASK_ID | jq .
echo ""

# Test 6: Update Task
echo -e "${GREEN}Test 6: Update Task${NC}"
echo "PUT $API_URL/tasks/$TASK_ID"
curl -s -X PUT $API_URL/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and snacks",
    "description": "Milk, eggs, bread, chips"
  }' | jq .
echo ""

# Test 7: List Tasks (should show 1 task)
echo -e "${GREEN}Test 7: List Tasks (Should show 1 task)${NC}"
echo "GET $API_URL/tasks"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks | jq .
echo ""

# Test 8: Mark Task as Complete
echo -e "${GREEN}Test 8: Mark Task as Complete${NC}"
echo "PATCH $API_URL/tasks/$TASK_ID/complete"
curl -s -X PATCH $API_URL/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# Test 9: Create another task
echo -e "${GREEN}Test 9: Create Second Task${NC}"
echo "POST $API_URL/tasks"
TASK2_RESPONSE=$(curl -s -X POST $API_URL/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write documentation",
    "description": null
  }')

echo "$TASK2_RESPONSE" | jq .
TASK2_ID=$(echo "$TASK2_RESPONSE" | jq -r '.id')
echo ""
echo "Created second task ID: $TASK2_ID"
echo ""

# Test 10: List Tasks (should show 2 tasks)
echo -e "${GREEN}Test 10: List Tasks (Should show 2 tasks)${NC}"
echo "GET $API_URL/tasks"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks | jq .
echo ""

# Test 11: Delete First Task
echo -e "${GREEN}Test 11: Delete First Task${NC}"
echo "DELETE $API_URL/tasks/$TASK_ID"
curl -s -X DELETE $API_URL/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"
echo ""

# Test 12: List Tasks (should show 1 task)
echo -e "${GREEN}Test 12: List Tasks (Should show 1 task)${NC}"
echo "GET $API_URL/tasks"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks | jq .
echo ""

# Test 13: Try to get deleted task (should 404)
echo -e "${GREEN}Test 13: Try to Get Deleted Task (Should 404)${NC}"
echo "GET $API_URL/tasks/$TASK_ID"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks/$TASK_ID -w "\nHTTP Status: %{http_code}\n" | jq .
echo ""

# Validation Tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}VALIDATION TESTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 14: Create task with empty title (should fail)
echo -e "${GREEN}Test 14: Create Task with Empty Title (Should fail with 422)${NC}"
echo "POST $API_URL/tasks"
curl -s -X POST $API_URL/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "   ",
    "description": "Test"
  }' -w "\nHTTP Status: %{http_code}\n" | jq .
echo ""

# Test 15: Create task with missing title (should fail)
echo -e "${GREEN}Test 15: Create Task without Title (Should fail with 422)${NC}"
echo "POST $API_URL/tasks"
curl -s -X POST $API_URL/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test"
  }' -w "\nHTTP Status: %{http_code}\n" | jq .
echo ""

# Test 16: Update task with invalid status (should fail)
echo -e "${GREEN}Test 16: Update Task with Invalid Status (Should fail with 422)${NC}"
echo "PUT $API_URL/tasks/$TASK2_ID"
curl -s -X PUT $API_URL/tasks/$TASK2_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in-progress"
  }' -w "\nHTTP Status: %{http_code}\n" | jq .
echo ""

# Cleanup: Delete remaining task
echo -e "${GREEN}Cleanup: Delete Remaining Task${NC}"
echo "DELETE $API_URL/tasks/$TASK2_ID"
curl -s -X DELETE $API_URL/tasks/$TASK2_ID \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"
echo ""

# Final check: List should be empty
echo -e "${GREEN}Final Check: List Tasks (Should be empty)${NC}"
echo "GET $API_URL/tasks"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tasks | jq .
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}All tests completed!${NC}"
echo -e "${BLUE}========================================${NC}"
