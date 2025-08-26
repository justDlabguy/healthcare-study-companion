#!/usr/bin/env python3
"""
Railway Deployment Validation Script

This script validates that the Railway deployment is properly configured
and all services are working correctly.
"""

import os
import sys
import requests
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def get_railway_url() -> Optional[str]:
    """Get the Railway deployment URL."""
    # Railway sets RAILWAY_STATIC_URL or we can construct it
    railway_url = os.getenv('RAILWAY_STATIC_URL')
    
    if not railway_url:
        # Try to construct from Railway environment
        railway_service = os.getenv('RAILWAY_SERVICE_NAME', 'web')
        railway_project = os.getenv('RAILWAY_PROJECT_NAME')
        
        if railway_project:
            railway_url = f"https://{railway_project}-{railway_service}.railway.app"
    
    return railway_url

def test_health_endpoint(base_url: str) -> Dict[str, Any]:
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{base_url}/healthz", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health endpoint responded: {health_data}")
            return {
                "passed": True,
                "status_code": response.status_code,
                "data": health_data,
                "response_time": response.elapsed.total_seconds()
            }
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return {
                "passed": False,
                "status_code": response.status_code,
                "error": response.text,
                "response_time": response.elapsed.total_seconds()
            }
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def test_root_endpoint(base_url: str) -> Dict[str, Any]:
    """Test the root endpoint."""
    print("🔍 Testing root endpoint...")
    
    try:
        response = requests.get(base_url, timeout=30)
        
        if response.status_code == 200:
            root_data = response.json()
            print(f"✅ Root endpoint responded: {root_data}")
            return {
                "passed": True,
                "status_code": response.status_code,
                "data": root_data,
                "response_time": response.elapsed.total_seconds()
            }
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return {
                "passed": False,
                "status_code": response.status_code,
                "error": response.text,
                "response_time": response.elapsed.total_seconds()
            }
            
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def test_docs_endpoint(base_url: str) -> Dict[str, Any]:
    """Test the API documentation endpoint."""
    print("🔍 Testing API docs endpoint...")
    
    try:
        response = requests.get(f"{base_url}/docs", timeout=30)
        
        if response.status_code == 200:
            print("✅ API docs endpoint accessible")
            return {
                "passed": True,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
        else:
            print(f"❌ API docs endpoint failed: {response.status_code}")
            return {
                "passed": False,
                "status_code": response.status_code,
                "error": response.text,
                "response_time": response.elapsed.total_seconds()
            }
            
    except Exception as e:
        print(f"❌ API docs endpoint test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def test_cors_configuration(base_url: str) -> Dict[str, Any]:
    """Test CORS configuration."""
    print("🔍 Testing CORS configuration...")
    
    try:
        # Test preflight request
        headers = {
            'Origin': 'https://example.com',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f"{base_url}/healthz", headers=headers, timeout=30)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        # Check if CORS is configured (at least one header present)
        has_cors = any(cors_headers.values())
        
        if has_cors:
            print("✅ CORS configuration detected")
            return {
                "passed": True,
                "cors_headers": cors_headers,
                "response_time": response.elapsed.total_seconds()
            }
        else:
            print("⚠️  No CORS headers detected")
            return {
                "passed": False,
                "error": "No CORS headers found",
                "response_time": response.elapsed.total_seconds()
            }
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def test_database_connectivity_via_api(base_url: str) -> Dict[str, Any]:
    """Test database connectivity through the API."""
    print("🔍 Testing database connectivity via API...")
    
    try:
        # The health endpoint includes database connectivity check
        response = requests.get(f"{base_url}/healthz", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            db_status = health_data.get('database', 'unknown')
            
            if db_status == 'connected':
                print("✅ Database connectivity confirmed via API")
                return {
                    "passed": True,
                    "database_status": db_status,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                print(f"❌ Database connectivity failed: {db_status}")
                return {
                    "passed": False,
                    "database_status": db_status,
                    "response_time": response.elapsed.total_seconds()
                }
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return {
                "passed": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def test_environment_configuration(base_url: str) -> Dict[str, Any]:
    """Test environment configuration through health endpoint."""
    print("🔍 Testing environment configuration...")
    
    try:
        response = requests.get(f"{base_url}/healthz", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            environment = health_data.get('environment', 'unknown')
            
            if environment == 'production':
                print("✅ Environment correctly set to production")
                return {
                    "passed": True,
                    "environment": environment,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                print(f"⚠️  Environment is '{environment}', expected 'production'")
                return {
                    "passed": False,
                    "environment": environment,
                    "warning": "Environment not set to production"
                }
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return {
                "passed": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def test_response_times(base_url: str) -> Dict[str, Any]:
    """Test API response times."""
    print("🔍 Testing API response times...")
    
    endpoints = [
        "/",
        "/healthz",
        "/docs"
    ]
    
    response_times = {}
    all_fast = True
    
    try:
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times[endpoint] = {
                "response_time_ms": response_time,
                "status_code": response.status_code
            }
            
            if response_time > 5000:  # More than 5 seconds
                all_fast = False
                print(f"⚠️  Slow response for {endpoint}: {response_time:.2f}ms")
            else:
                print(f"✅ {endpoint}: {response_time:.2f}ms")
        
        avg_response_time = sum(rt["response_time_ms"] for rt in response_times.values()) / len(response_times)
        
        return {
            "passed": all_fast,
            "response_times": response_times,
            "average_response_time_ms": avg_response_time
        }
        
    except Exception as e:
        print(f"❌ Response time test failed: {e}")
        return {
            "passed": False,
            "error": str(e)
        }

def generate_deployment_report(base_url: str) -> Dict[str, Any]:
    """Generate a comprehensive deployment validation report."""
    print("🚀 Healthcare Study Companion - Railway Deployment Validation")
    print("=" * 70)
    print(f"Testing URL: {base_url}")
    print("=" * 70)
    
    tests = [
        ("Health Endpoint", lambda: test_health_endpoint(base_url)),
        ("Root Endpoint", lambda: test_root_endpoint(base_url)),
        ("API Documentation", lambda: test_docs_endpoint(base_url)),
        ("CORS Configuration", lambda: test_cors_configuration(base_url)),
        ("Database Connectivity", lambda: test_database_connectivity_via_api(base_url)),
        ("Environment Configuration", lambda: test_environment_configuration(base_url)),
        ("Response Times", lambda: test_response_times(base_url))
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result
            if not result.get("passed", False):
                all_passed = False
        except Exception as e:
            results[test_name] = {
                "passed": False,
                "error": str(e)
            }
            all_passed = False
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for r in results.values() if r.get("passed", False))
    total_count = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
        print(f"{status} {test_name}")
        if result.get("error"):
            print(f"     Error: {result['error']}")
        elif result.get("warning"):
            print(f"     Warning: {result['warning']}")
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if all_passed:
        print("🎉 All deployment validation tests passed! Railway deployment is ready.")
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
    
    # Generate report
    report = {
        "timestamp": time.time(),
        "base_url": base_url,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "railway_deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID"),
        "tests": results,
        "summary": {
            "total_tests": total_count,
            "passed_tests": passed_count,
            "all_passed": all_passed
        }
    }
    
    return report

def save_report(report: Dict[str, Any]):
    """Save the deployment validation report."""
    try:
        logs_dir = backend_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        report_file = logs_dir / "railway_deployment_validation.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
        
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")

def main():
    """Main function to run deployment validation."""
    # Get Railway URL
    base_url = get_railway_url()
    
    if not base_url:
        # Try to get from command line argument
        if len(sys.argv) > 1:
            base_url = sys.argv[1]
        else:
            print("❌ Could not determine Railway URL.")
            print("Usage: python validate_railway_deployment.py [URL]")
            print("Or set RAILWAY_STATIC_URL environment variable")
            sys.exit(1)
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    try:
        # Run validation tests
        report = generate_deployment_report(base_url)
        
        # Save report
        save_report(report)
        
        # Exit with appropriate code
        if report["summary"]["all_passed"]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error during deployment validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()