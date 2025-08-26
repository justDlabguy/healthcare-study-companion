#!/bin/bash

# Comprehensive Environment Validation Script
# This script validates environment configuration for both backend and frontend
# across all environments (development, staging, production)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENTS=("development" "staging" "production")
STRICT_MODE=false
VERBOSE=false
JSON_OUTPUT=false
EXIT_CODE=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --strict|-s)
            STRICT_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --environment|-e)
            ENVIRONMENTS=("$2")
            shift 2
            ;;
        --help|-h)
            echo "Environment Validation Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --environment, -e ENV  Validate specific environment only"
            echo "  --strict, -s           Fail on warnings (useful for CI/CD)"
            echo "  --verbose, -v          Show detailed output"
            echo "  --json                 Output results in JSON format"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Environments: development, staging, production"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    if [[ $JSON_OUTPUT == false ]]; then
        echo -e "${color}${message}${NC}"
    fi
}

# Function to validate backend environment
validate_backend() {
    local env=$1
    local args=""
    
    if [[ $STRICT_MODE == true ]]; then
        args="$args --strict"
    fi
    
    if [[ $VERBOSE == true ]]; then
        args="$args --verbose"
    fi
    
    if [[ $JSON_OUTPUT == true ]]; then
        args="$args --json"
    fi
    
    print_status $BLUE "🔍 Validating backend environment: $env"
    
    cd backend
    if python scripts/validate_environment.py --environment "$env" $args; then
        print_status $GREEN "✅ Backend $env validation passed"
        cd ..
        return 0
    else
        print_status $RED "❌ Backend $env validation failed"
        cd ..
        return 1
    fi
}

# Function to validate frontend environment
validate_frontend() {
    local env=$1
    local args=""
    
    if [[ $STRICT_MODE == true ]]; then
        args="$args --strict"
    fi
    
    if [[ $VERBOSE == true ]]; then
        args="$args --verbose"
    fi
    
    if [[ $JSON_OUTPUT == true ]]; then
        args="$args --json"
    fi
    
    print_status $BLUE "🔍 Validating frontend environment: $env"
    
    cd frontend
    if node scripts/validate-environment.js --environment "$env" $args; then
        print_status $GREEN "✅ Frontend $env validation passed"
        cd ..
        return 0
    else
        print_status $RED "❌ Frontend $env validation failed"
        cd ..
        return 1
    fi
}

# Function to check if required files exist
check_prerequisites() {
    local missing_files=()
    
    # Check backend files
    if [[ ! -f "backend/scripts/validate_environment.py" ]]; then
        missing_files+=("backend/scripts/validate_environment.py")
    fi
    
    if [[ ! -f "backend/app/config.py" ]]; then
        missing_files+=("backend/app/config.py")
    fi
    
    # Check frontend files
    if [[ ! -f "frontend/scripts/validate-environment.js" ]]; then
        missing_files+=("frontend/scripts/validate-environment.js")
    fi
    
    # Check environment files
    for env in "${ENVIRONMENTS[@]}"; do
        if [[ ! -f "backend/.env.$env" ]]; then
            missing_files+=("backend/.env.$env")
        fi
        
        if [[ ! -f "frontend/.env.$env" ]]; then
            missing_files+=("frontend/.env.$env")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        print_status $RED "❌ Missing required files:"
        for file in "${missing_files[@]}"; do
            print_status $RED "   - $file"
        done
        return 1
    fi
    
    return 0
}

# Function to generate summary report
generate_summary() {
    local total_validations=$1
    local passed_validations=$2
    local failed_validations=$3
    
    if [[ $JSON_OUTPUT == false ]]; then
        echo ""
        print_status $BLUE "📊 Validation Summary"
        echo "   Total validations: $total_validations"
        echo "   Passed: $passed_validations"
        echo "   Failed: $failed_validations"
        echo ""
        
        if [[ $failed_validations -eq 0 ]]; then
            print_status $GREEN "🎉 All environment validations passed!"
        else
            print_status $RED "💥 $failed_validations environment validation(s) failed!"
            print_status $YELLOW "   Please fix the issues above before deploying."
        fi
    fi
}

# Main execution
main() {
    print_status $BLUE "🚀 Starting comprehensive environment validation"
    print_status $BLUE "   Environments: ${ENVIRONMENTS[*]}"
    print_status $BLUE "   Strict mode: $STRICT_MODE"
    print_status $BLUE "   Verbose: $VERBOSE"
    echo ""
    
    # Check prerequisites
    if ! check_prerequisites; then
        print_status $RED "❌ Prerequisites check failed"
        exit 1
    fi
    
    local total_validations=0
    local passed_validations=0
    local failed_validations=0
    
    # Validate each environment
    for env in "${ENVIRONMENTS[@]}"; do
        print_status $YELLOW "🔄 Validating environment: $env"
        echo ""
        
        # Validate backend
        total_validations=$((total_validations + 1))
        if validate_backend "$env"; then
            passed_validations=$((passed_validations + 1))
        else
            failed_validations=$((failed_validations + 1))
            EXIT_CODE=1
        fi
        
        echo ""
        
        # Validate frontend
        total_validations=$((total_validations + 1))
        if validate_frontend "$env"; then
            passed_validations=$((passed_validations + 1))
        else
            failed_validations=$((failed_validations + 1))
            EXIT_CODE=1
        fi
        
        echo ""
        print_status $BLUE "─────────────────────────────────────────"
        echo ""
    done
    
    # Generate summary
    generate_summary $total_validations $passed_validations $failed_validations
    
    exit $EXIT_CODE
}

# Run main function
main "$@"