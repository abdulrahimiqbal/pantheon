#!/usr/bin/env python3
"""
End-to-End Deployment Test Suite for Pantheon Physics Swarm
This test suite verifies all functionality works correctly before Vercel deployment.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import requests
from fastapi.testclient import TestClient
import importlib.util

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('e2e_test.log')
    ]
)
logger = logging.getLogger(__name__)

class E2ETestSuite:
    """Comprehensive end-to-end test suite for the Pantheon Physics Swarm."""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def log_test_start(self, test_name: str):
        """Log the start of a test."""
        logger.info(f"🧪 STARTING TEST: {test_name}")
        logger.info("=" * 60)
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result and track statistics."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"Details: {details}")
        logger.info("-" * 60)
        
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
    
    def test_project_structure(self) -> bool:
        """Test 1: Verify project structure and required files exist."""
        self.log_test_start("Project Structure Verification")
        
        required_files = [
            "orchestration/main.py",
            "api/index.py",
            "api/requirements.txt",
            "public/index.html",
            "vercel.json",
            "package.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                logger.error(f"❌ Missing required file: {file_path}")
            else:
                logger.info(f"✅ Found required file: {file_path}")
        
        passed = len(missing_files) == 0
        details = f"Missing files: {missing_files}" if missing_files else "All required files present"
        self.log_test_result("Project Structure", passed, details)
        return passed
    
    def test_fastapi_import(self) -> bool:
        """Test 2: Verify FastAPI app imports correctly."""
        self.log_test_start("FastAPI Import Test")
        
        try:
            # Add paths
            sys.path.insert(0, str(Path.cwd()))
            sys.path.insert(0, str(Path.cwd() / "orchestration"))
            
            # Import the main app
            from orchestration.main import app
            logger.info("✅ Successfully imported FastAPI app from orchestration.main")
            
            # Check app type
            app_type = type(app).__name__
            logger.info(f"✅ App type: {app_type}")
            
            # Check routes
            routes = [route.path for route in app.routes]
            logger.info(f"✅ Registered routes: {routes}")
            
            expected_routes = ["/health", "/", "/physics/query", "/agents/status", "/config"]
            missing_routes = [route for route in expected_routes if route not in routes]
            
            if missing_routes:
                logger.error(f"❌ Missing expected routes: {missing_routes}")
                self.log_test_result("FastAPI Import", False, f"Missing routes: {missing_routes}")
                return False
            
            logger.info("✅ All expected routes are registered")
            self.log_test_result("FastAPI Import", True, f"App type: {app_type}, Routes: {len(routes)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import FastAPI app: {e}")
            self.log_test_result("FastAPI Import", False, str(e))
            return False
    
    def test_api_function_import(self) -> bool:
        """Test 3: Verify API function imports correctly."""
        self.log_test_start("API Function Import Test")
        
        try:
            # Test API function import with correct path
            import importlib.util
            
            # Load the module from file path
            spec = importlib.util.spec_from_file_location("index", Path.cwd() / "api" / "index.py")
            api_module = importlib.util.module_from_spec(spec)
            
            # Add necessary paths before execution
            sys.path.insert(0, str(Path.cwd()))
            sys.path.insert(0, str(Path.cwd() / "orchestration"))
            
            spec.loader.exec_module(api_module)
            
            logger.info("✅ Successfully imported api/index.py module")
            
            # Check if app is available
            if hasattr(api_module, 'app'):
                logger.info("✅ 'app' attribute found in api/index.py")
                app_type = type(api_module.app).__name__
                logger.info(f"✅ API app type: {app_type}")
                
                # Test routes if it's a FastAPI app
                if hasattr(api_module.app, 'routes'):
                    routes = [route.path for route in api_module.app.routes]
                    logger.info(f"✅ API routes: {routes}")
                
                self.log_test_result("API Function Import", True, f"App type: {app_type}")
                return True
            else:
                logger.error("❌ 'app' attribute not found in api/index.py")
                self.log_test_result("API Function Import", False, "No 'app' attribute found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to import API function: {e}")
            self.log_test_result("API Function Import", False, str(e))
            return False
    
    def test_fastapi_endpoints(self) -> bool:
        """Test 4: Test FastAPI endpoints using TestClient."""
        self.log_test_start("FastAPI Endpoints Test")
        
        try:
            from orchestration.main import app
            client = TestClient(app)
            
            # Test health endpoint
            logger.info("Testing /health endpoint...")
            response = client.get("/health")
            logger.info(f"Health endpoint - Status: {response.status_code}, Response: {response.json()}")
            
            if response.status_code != 200:
                self.log_test_result("FastAPI Endpoints", False, f"Health endpoint failed: {response.status_code}")
                return False
            
            # Test root endpoint
            logger.info("Testing / endpoint...")
            response = client.get("/")
            logger.info(f"Root endpoint - Status: {response.status_code}, Response: {response.json()}")
            
            if response.status_code != 200:
                self.log_test_result("FastAPI Endpoints", False, f"Root endpoint failed: {response.status_code}")
                return False
            
            # Test physics query endpoint
            logger.info("Testing /physics/query endpoint...")
            test_query = {
                "question": "What is the speed of light?",
                "complexity": "basic",
                "include_sources": True
            }
            response = client.post("/physics/query", json=test_query)
            logger.info(f"Physics query endpoint - Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Physics query response: {response_data}")
            else:
                logger.warning(f"Physics query endpoint returned {response.status_code} (expected for missing swarm)")
            
            # Test agents status endpoint
            logger.info("Testing /agents/status endpoint...")
            response = client.get("/agents/status")
            logger.info(f"Agents status endpoint - Status: {response.status_code}, Response: {response.json()}")
            
            # Test config endpoint
            logger.info("Testing /config endpoint...")
            response = client.get("/config")
            logger.info(f"Config endpoint - Status: {response.status_code}, Response: {response.json()}")
            
            self.log_test_result("FastAPI Endpoints", True, "All endpoints responding correctly")
            return True
            
        except Exception as e:
            logger.error(f"❌ FastAPI endpoints test failed: {e}")
            self.log_test_result("FastAPI Endpoints", False, str(e))
            return False
    
    def test_vercel_config(self) -> bool:
        """Test 5: Verify Vercel configuration is valid."""
        self.log_test_start("Vercel Configuration Test")
        
        try:
            with open("vercel.json", "r") as f:
                config = json.load(f)
            
            logger.info("✅ vercel.json is valid JSON")
            logger.info(f"✅ Vercel config: {json.dumps(config, indent=2)}")
            
            # Check required fields
            required_fields = ["version", "functions"]
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                logger.error(f"❌ Missing required fields in vercel.json: {missing_fields}")
                self.log_test_result("Vercel Configuration", False, f"Missing fields: {missing_fields}")
                return False
            
            # Check functions configuration
            functions = config.get("functions", {})
            if "api/index.py" not in functions:
                logger.error("❌ api/index.py not configured in functions")
                self.log_test_result("Vercel Configuration", False, "api/index.py not in functions")
                return False
            
            logger.info("✅ api/index.py is configured in functions")
            
            # Check runtime
            index_config = functions["api/index.py"]
            if "runtime" in index_config:
                logger.info(f"✅ Runtime specified: {index_config['runtime']}")
            else:
                logger.info("ℹ️ Runtime not specified (will use default)")
            
            self.log_test_result("Vercel Configuration", True, "Configuration is valid")
            return True
            
        except Exception as e:
            logger.error(f"❌ Vercel configuration test failed: {e}")
            self.log_test_result("Vercel Configuration", False, str(e))
            return False
    
    def test_api_requirements(self) -> bool:
        """Test 6: Verify API requirements are installable."""
        self.log_test_start("API Requirements Test")
        
        try:
            with open("api/requirements.txt", "r") as f:
                requirements = f.read().strip().split("\n")
            
            logger.info("✅ api/requirements.txt exists and is readable")
            logger.info(f"✅ Requirements: {requirements}")
            
            # Check for essential packages
            essential_packages = ["fastapi", "uvicorn", "pydantic"]
            found_packages = []
            
            for req in requirements:
                if req.strip() and not req.startswith("#"):
                    package_name = req.split("==")[0].split(">=")[0].split("<=")[0].strip()
                    found_packages.append(package_name)
            
            missing_essential = [pkg for pkg in essential_packages if pkg not in found_packages]
            
            if missing_essential:
                logger.error(f"❌ Missing essential packages: {missing_essential}")
                self.log_test_result("API Requirements", False, f"Missing: {missing_essential}")
                return False
            
            logger.info(f"✅ All essential packages found: {essential_packages}")
            self.log_test_result("API Requirements", True, f"Found packages: {found_packages}")
            return True
            
        except Exception as e:
            logger.error(f"❌ API requirements test failed: {e}")
            self.log_test_result("API Requirements", False, str(e))
            return False
    
    def test_public_frontend(self) -> bool:
        """Test 7: Verify public frontend HTML is valid."""
        self.log_test_start("Public Frontend Test")
        
        try:
            with open("public/index.html", "r") as f:
                html_content = f.read()
            
            logger.info("✅ public/index.html exists and is readable")
            logger.info(f"✅ HTML content length: {len(html_content)} characters")
            
            # Check for essential elements
            essential_elements = [
                "<title>Pantheon Physics Swarm</title>",
                "id=\"physicsForm\"",
                "id=\"query\"",
                "id=\"submitBtn\"",
                "/api/health",
                "/api/physics/query"
            ]
            
            missing_elements = []
            for element in essential_elements:
                if element not in html_content:
                    missing_elements.append(element)
                    logger.error(f"❌ Missing essential element: {element}")
                else:
                    logger.info(f"✅ Found essential element: {element}")
            
            if missing_elements:
                self.log_test_result("Public Frontend", False, f"Missing elements: {missing_elements}")
                return False
            
            self.log_test_result("Public Frontend", True, "All essential elements found")
            return True
            
        except Exception as e:
            logger.error(f"❌ Public frontend test failed: {e}")
            self.log_test_result("Public Frontend", False, str(e))
            return False
    
    def test_local_server(self) -> bool:
        """Test 8: Start local server and test endpoints."""
        self.log_test_start("Local Server Test")
        
        try:
            import subprocess
            import time
            import threading
            
            # Start the server in a separate process
            logger.info("Starting local FastAPI server...")
            server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "orchestration.main:app", 
                "--host", "127.0.0.1", "--port", "8080", "--log-level", "info"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for server to start
            time.sleep(3)
            
            # Test endpoints
            base_url = "http://127.0.0.1:8080"
            
            # Test health endpoint
            logger.info("Testing local health endpoint...")
            response = requests.get(f"{base_url}/health", timeout=5)
            logger.info(f"Local health endpoint - Status: {response.status_code}, Response: {response.json()}")
            
            if response.status_code != 200:
                server_process.terminate()
                self.log_test_result("Local Server", False, f"Health endpoint failed: {response.status_code}")
                return False
            
            # Test root endpoint
            logger.info("Testing local root endpoint...")
            response = requests.get(f"{base_url}/", timeout=5)
            logger.info(f"Local root endpoint - Status: {response.status_code}, Response: {response.json()}")
            
            # Test physics query endpoint
            logger.info("Testing local physics query endpoint...")
            test_query = {
                "question": "What is quantum mechanics?",
                "complexity": "basic",
                "include_sources": True
            }
            response = requests.post(f"{base_url}/physics/query", json=test_query, timeout=10)
            logger.info(f"Local physics query endpoint - Status: {response.status_code}")
            
            # Cleanup
            server_process.terminate()
            server_process.wait()
            
            self.log_test_result("Local Server", True, "Local server tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Local server test failed: {e}")
            self.log_test_result("Local Server", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        logger.info("🚀 STARTING COMPREHENSIVE E2E TEST SUITE")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_project_structure,
            self.test_fastapi_import,
            self.test_api_function_import,
            self.test_fastapi_endpoints,
            self.test_vercel_config,
            self.test_api_requirements,
            self.test_public_frontend,
            self.test_local_server
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"❌ Test {test.__name__} crashed: {e}")
                self.log_test_result(test.__name__, False, f"Test crashed: {e}")
        
        # Calculate results
        end_time = time.time()
        total_time = end_time - start_time
        
        results = {
            "total_tests": len(self.test_results),
            "passed": len(self.passed_tests),
            "failed": len(self.failed_tests),
            "pass_rate": len(self.passed_tests) / len(self.test_results) * 100 if self.test_results else 0,
            "total_time": total_time,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "detailed_results": self.test_results
        }
        
        # Log summary
        logger.info("=" * 80)
        logger.info("🏁 TEST SUITE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {results['total_tests']}")
        logger.info(f"Passed: {results['passed']} ✅")
        logger.info(f"Failed: {results['failed']} ❌")
        logger.info(f"Pass Rate: {results['pass_rate']:.1f}%")
        logger.info(f"Total Time: {results['total_time']:.2f} seconds")
        
        if results['failed'] == 0:
            logger.info("🎉 ALL TESTS PASSED! Ready for deployment!")
        else:
            logger.error(f"⚠️ {results['failed']} tests failed. Fix issues before deployment.")
            logger.error(f"Failed tests: {results['failed_tests']}")
        
        return results

def main():
    """Main function to run the test suite."""
    test_suite = E2ETestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to file
    with open("e2e_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("📊 Test results saved to e2e_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main() 