#!/bin/bash
# Test runner script for Knowledge Vault

echo "=========================================="
echo "🧪 Knowledge Vault - Running Tests"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run pytest with coverage
echo ""
echo "Running pytest with coverage..."
pytest tests/ -v --tb=short --cov=src --cov-report=term --cov-report=html

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi
