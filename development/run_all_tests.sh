#!/bin/bash

# 🧪 AUTOMATED TESTING SCRIPT FOR TRADING AI SYSTEM
# Script untuk menjalankan semua test files Python di folder tests/
# Created: July 17, 2025

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

print_color $BLUE "🧪 AUTOMATED TESTING SCRIPT - TRADING AI SYSTEM"
print_color $BLUE "=" $(printf '=%.0s' {1..60})

# Check if tests directory exists
if [ ! -d "tests" ]; then
    print_color $RED "❌ Error: tests/ directory not found!"
    print_color $YELLOW "Please create tests/ directory and place test files there."
    exit 1
fi

# Check if there are any test files
test_files=$(find tests/ -name "test_*.py" -type f | wc -l)
if [ $test_files -eq 0 ]; then
    print_color $RED "❌ Error: No test files found in tests/ directory!"
    print_color $YELLOW "Please place test_*.py files in tests/ directory."
    exit 1
fi

print_color $GREEN "📁 Found $test_files test files in tests/ directory"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_color $RED "❌ WARNING: pytest is not installed!"
    print_color $YELLOW "Please install pytest using: pip install pytest"
    print_color $YELLOW "Attempting to run with python -m pytest..."
    
    # Try to run with python -m pytest
    if ! python -m pytest --version &> /dev/null; then
        print_color $RED "❌ ERROR: pytest is not available!"
        print_color $YELLOW "Please install pytest first: pip install pytest"
        exit 1
    fi
    
    PYTEST_CMD="python -m pytest"
else
    PYTEST_CMD="pytest"
    print_color $GREEN "✅ pytest is installed"
fi

# Check if pytest-cov is available for coverage
COVERAGE_AVAILABLE=false
if $PYTEST_CMD --version | grep -q "pytest-cov" 2>/dev/null || python -c "import pytest_cov" 2>/dev/null; then
    COVERAGE_AVAILABLE=true
    print_color $GREEN "✅ pytest-cov is available - coverage will be included"
else
    print_color $YELLOW "⚠️  pytest-cov not available - running without coverage"
fi

print_color $BLUE "=" $(printf '=%.0s' {1..60})

# List all test files that will be executed
print_color $BLUE "📋 Test files to be executed:"
find tests/ -name "test_*.py" -type f | sort | while read -r file; do
    print_color $BLUE "   - $file"
done

print_color $BLUE "=" $(printf '=%.0s' {1..60})

# Build pytest command
PYTEST_ARGS="tests/ --tb=short --maxfail=3 --disable-warnings -v"

# Add coverage if available
if [ "$COVERAGE_AVAILABLE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=. --cov-report=term-missing"
fi

# Execute tests
print_color $GREEN "🚀 Running tests with command: $PYTEST_CMD $PYTEST_ARGS"
print_color $BLUE "=" $(printf '=%.0s' {1..60})

# Run the tests and capture exit code
$PYTEST_CMD $PYTEST_ARGS
test_exit_code=$?

print_color $BLUE "=" $(printf '=%.0s' {1..60})

# Display results based on exit code
if [ $test_exit_code -eq 0 ]; then
    print_color $GREEN "🎉 ALL TESTS PASSED SUCCESSFULLY!"
elif [ $test_exit_code -eq 1 ]; then
    print_color $RED "❌ SOME TESTS FAILED"
elif [ $test_exit_code -eq 2 ]; then
    print_color $RED "❌ TEST EXECUTION INTERRUPTED"
elif [ $test_exit_code -eq 3 ]; then
    print_color $RED "❌ INTERNAL ERROR OCCURRED"
elif [ $test_exit_code -eq 4 ]; then
    print_color $RED "❌ PYTEST USAGE ERROR"
elif [ $test_exit_code -eq 5 ]; then
    print_color $RED "❌ NO TESTS FOUND"
else
    print_color $RED "❌ UNKNOWN ERROR (exit code: $test_exit_code)"
fi

# Display summary
print_color $BLUE "📊 TESTING SUMMARY:"
print_color $BLUE "   - Test files found: $test_files"
print_color $BLUE "   - Pytest command: $PYTEST_CMD"
print_color $BLUE "   - Coverage enabled: $COVERAGE_AVAILABLE"
print_color $BLUE "   - Exit code: $test_exit_code"
print_color $BLUE "   - Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

print_color $BLUE "=" $(printf '=%.0s' {1..60})

# Exit with the same code as pytest
exit $test_exit_code