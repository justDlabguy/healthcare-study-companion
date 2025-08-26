#!/usr/bin/env python3
"""
Simple script to run tests with coverage reporting locally.
"""
import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pytest
        import coverage
        return True
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("\n💡 To install dependencies, run:")
        print("   pip install -r requirements.txt")
        print("\n   Or install coverage dependencies specifically:")
        print("   pip install pytest pytest-cov coverage")
        return False


def setup_test_environment():
    """Set up test environment variables."""
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["MISTRAL_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["JWT_SECRET"] = "test-secret-key-for-testing-purposes-only"
    os.environ["LLM_PROVIDER"] = "mistral"
    os.environ["LLM_MODEL_ID"] = "mistral-small"
    os.environ["EMBEDDING_MODEL_ID"] = "mistral-embed"


def run_coverage():
    """Run tests with coverage reporting."""
    print("🧪 Running tests with coverage reporting...")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Set up environment
    setup_test_environment()
    
    # Check if pytest-cov is available
    try:
        result = subprocess.run([sys.executable, "-c", "import pytest_cov"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ pytest-cov not found. Installing coverage dependencies...")
            install_result = subprocess.run([
                sys.executable, "-m", "pip", "install", "pytest-cov", "coverage"
            ], capture_output=True, text=True)
            
            if install_result.returncode != 0:
                print("❌ Failed to install pytest-cov. Please install manually:")
                print("   pip install pytest-cov coverage")
                return 1
            else:
                print("✅ pytest-cov installed successfully")
    except Exception as e:
        print(f"⚠️  Could not check pytest-cov: {e}")
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-branch",
        "--cov-fail-under=80",
        "-v"
    ]
    
    try:
        print("Running command:", " ".join(cmd))
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        print("\n" + "=" * 60)
        
        if result.returncode == 0:
            print("✅ Tests passed and coverage threshold met!")
            print("\n📊 Coverage reports generated:")
            print("  - Terminal: Displayed above")
            print("  - HTML: htmlcov/index.html")
            print("  - XML: coverage.xml")
            print("  - JSON: Use 'coverage json' to generate")
        else:
            print("❌ Tests failed or coverage threshold not met")
            print("Check the output above for details.")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  Coverage run interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python run_coverage.py")
        print("Run tests with coverage reporting and generate reports.")
        print("\nGenerated reports:")
        print("  - Terminal output with missing lines")
        print("  - HTML report in htmlcov/ directory")
        print("  - XML report (coverage.xml)")
        print("  - JSON report (use 'coverage json' command)")
        print("\nMinimum coverage threshold: 80%")
        return 0
    
    return run_coverage()


if __name__ == "__main__":
    sys.exit(main())