#!/usr/bin/env python3
"""
Install coverage dependencies and verify setup.
"""
import subprocess
import sys
import os


def install_coverage_dependencies():
    """Install coverage-related dependencies."""
    print("📦 Installing coverage dependencies...")
    
    dependencies = [
        "pytest-cov==4.0.0",
        "coverage==7.6.1"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, check=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    return True


def verify_installation():
    """Verify that coverage tools are properly installed."""
    print("\n🔍 Verifying installation...")
    
    try:
        import pytest
        print("✅ pytest available")
    except ImportError:
        print("❌ pytest not available")
        return False
    
    try:
        import coverage
        print("✅ coverage available")
    except ImportError:
        print("❌ coverage not available")
        return False
    
    try:
        import pytest_cov
        print("✅ pytest-cov available")
    except ImportError:
        print("❌ pytest-cov not available")
        return False
    
    # Test pytest-cov integration
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--help"
        ], capture_output=True, text=True)
        
        if "--cov" in result.stdout:
            print("✅ pytest-cov integration working")
            return True
        else:
            print("❌ pytest-cov not integrated with pytest")
            return False
            
    except Exception as e:
        print(f"❌ Error testing pytest-cov integration: {e}")
        return False


def main():
    """Main installation and verification process."""
    print("🚀 Coverage Dependencies Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_coverage_dependencies():
        print("\n❌ Installation failed")
        return 1
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Verification failed")
        return 1
    
    print("\n✅ Coverage setup complete!")
    print("\nYou can now run:")
    print("  python run_coverage.py")
    print("  pytest --cov=app --cov-report=term-missing")
    print("  python scripts/coverage_config.py test")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())