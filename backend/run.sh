#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default environment
ENV="development"

# Function to display help
show_help() {
    echo -e "${YELLOW}Usage: $0 [command] [options]${NC}"
    echo ""
    echo "Commands:"
    echo "  install             Install project dependencies"
    echo "  setup               Setup development environment"
    echo "  migrate [--upgrade|--downgrade]  Run database migrations"
    echo "  start               Start the application"
    echo "  test                Run tests"
    echo "  coverage            Run tests with coverage report"
    echo "  lint                Run code linter"
    echo "  help                Show this help message"
    echo ""
    echo "Options:"
    echo "  --env               Set environment (development|staging|production)"
    echo ""
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --env)
            ENV="$2"
            shift # past argument
            shift # past value
            ;;
        -h|--help)
            show_help
            ;;
        *)
            COMMAND="$1"
            shift
            break
            ;;
    esac
done

# Set environment variables
export PYTHONPATH="$(pwd)"

# Function to load environment variables
load_env() {
    if [ -f ".env.$ENV" ]; then
        echo -e "${GREEN}Loading .env.$ENV...${NC}"
        export $(grep -v '^#' ".env.$ENV" | xargs)
    else
        echo -e "${YELLOW}Warning: .env.$ENV not found, using system environment variables${NC}"
    fi
}

# Function to install dependencies
install_deps() {
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
}

# Function to setup development environment
setup_dev() {
    echo -e "${GREEN}Setting up development environment...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${GREEN}Creating virtual environment...${NC}"
        python -m venv venv
        source venv/bin/activate
        install_deps
    else
        echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
        source venv/bin/activate
    fi
    
    # Create uploads directory if it doesn't exist
    mkdir -p uploads
    
    echo -e "${GREEN}Development environment setup complete!${NC}"
}

# Function to run database migrations
run_migrations() {
    load_env
    echo -e "${GREEN}Running database migrations...${NC}"
    
    case "$1" in
        --upgrade)
            alembic upgrade head
            ;;
        --downgrade)
            alembic downgrade -1
            ;;
        *)
            echo -e "${YELLOW}No migration operation specified. Use --upgrade or --downgrade${NC}"
            exit 1
            ;;
    esac
}

# Function to start the application
start_app() {
    load_env
    echo -e "${GREEN}Starting $ENV server...${NC}"
    
    if [ "$ENV" = "production" ]; then
        uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 --proxy-headers
    else
        uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
    fi
}

# Function to run tests
run_tests() {
    load_env
    echo -e "${GREEN}Running tests...${NC}"
    python -m pytest tests/ -v
}

# Function to run tests with coverage
run_coverage() {
    load_env
    echo -e "${GREEN}Running tests with coverage...${NC}"
    python -m pytest --cov=app --cov-report=term-missing --cov-report=html tests/
}

# Function to run linter
run_lint() {
    echo -e "${GREEN}Running linter...${NC}"
    flake8 app/ tests/
}

# Main command handler
case "$COMMAND" in
    install)
        install_deps
        ;;
    setup)
        setup_dev
        ;;
    migrate)
        run_migrations "$@"
        ;;
    start)
        start_app
        ;;
    test)
        run_tests
        ;;
    coverage)
        run_coverage
        ;;
    lint)
        run_lint
        ;;
    help|*)
        show_help
        ;;
esac

exit 0
