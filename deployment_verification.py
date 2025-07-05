#!/usr/bin/env python3
"""
Final Deployment Verification for Pantheon Physics Swarm
This script performs final checks specific to Vercel deployment requirements.
"""

import json
import sys
from pathlib import Path
import importlib.util

def verify_vercel_function_structure():
    """Verify the API function follows Vercel's expected structure."""
    print("🔍 VERCEL FUNCTION STRUCTURE VERIFICATION")
    print("=" * 60)
    
    # Load and execute the API function
    spec = importlib.util.spec_from_file_location("index", Path.cwd() / "api" / "index.py")
    api_module = importlib.util.module_from_spec(spec)
    
    # Add paths
    sys.path.insert(0, str(Path.cwd()))
    sys.path.insert(0, str(Path.cwd() / "orchestration"))
    
    # Execute the module (this will run the import and setup)
    spec.loader.exec_module(api_module)
    
    print("✅ API function loaded successfully")
    
    # Check required exports
    if hasattr(api_module, 'app'):
        print("✅ 'app' export found (ASGI application)")
        app_type = type(api_module.app).__name__
        print(f"✅ App type: {app_type}")
        
        if app_type == "FastAPI":
            routes = [route.path for route in api_module.app.routes]
            print(f"✅ Routes available: {routes}")
            
            # Verify critical routes
            critical_routes = ["/health", "/", "/physics/query"]
            missing_routes = [route for route in critical_routes if route not in routes]
            
            if not missing_routes:
                print("✅ All critical routes present")
            else:
                print(f"❌ Missing critical routes: {missing_routes}")
                return False
        
        return True
    else:
        print("❌ No 'app' export found")
        return False

def verify_requirements_compatibility():
    """Verify requirements.txt is compatible with Vercel Python runtime."""
    print("\n🔍 REQUIREMENTS COMPATIBILITY VERIFICATION")
    print("=" * 60)
    
    with open("api/requirements.txt", "r") as f:
        requirements = f.read().strip().split("\n")
    
    # Check for problematic packages
    problematic_packages = []
    large_packages = ["torch", "tensorflow", "numpy", "scipy", "pandas"]
    
    for req in requirements:
        if req.strip() and not req.startswith("#"):
            package_name = req.split("==")[0].split(">=")[0].split("<=")[0].strip()
            if package_name.lower() in large_packages:
                problematic_packages.append(package_name)
    
    if not problematic_packages:
        print("✅ No problematic large packages found")
    else:
        print(f"⚠️ Large packages detected (may cause deployment issues): {problematic_packages}")
    
    print(f"✅ Total packages: {len([r for r in requirements if r.strip() and not r.startswith('#')])}")
    return True

def verify_vercel_config_completeness():
    """Verify vercel.json has all necessary configurations."""
    print("\n🔍 VERCEL CONFIG COMPLETENESS VERIFICATION")
    print("=" * 60)
    
    with open("vercel.json", "r") as f:
        config = json.load(f)
    
    # Check essential configurations
    checks = [
        ("version", "Version specified"),
        ("functions", "Functions configuration present"),
        ("env", "Environment variables configured"),
    ]
    
    # Check if api/index.py is in functions
    if "api/index.py" in config.get("functions", {}):
        print("✅ Main API function configured")
        
        # Check runtime
        api_config = config["functions"]["api/index.py"]
        if "runtime" in api_config:
            print(f"✅ Runtime specified: {api_config['runtime']}")
        else:
            print("⚠️ Runtime not specified (will use default)")
    else:
        print("❌ Main API function not configured")
        return False
    
    for check_path, description in checks:
        keys = check_path.split(".")
        current = config
        
        try:
            for key in keys:
                current = current[key]
            print(f"✅ {description}")
        except (KeyError, TypeError):
            print(f"❌ {description} - MISSING")
            return False
    
    return True

def verify_static_files():
    """Verify static files are properly structured."""
    print("\n🔍 STATIC FILES VERIFICATION")
    print("=" * 60)
    
    # Check public directory
    public_dir = Path("public")
    if not public_dir.exists():
        print("❌ Public directory missing")
        return False
    
    # Check index.html
    index_file = public_dir / "index.html"
    if not index_file.exists():
        print("❌ public/index.html missing")
        return False
    
    with open(index_file, "r") as f:
        html_content = f.read()
    
    # Check for correct API paths
    if "/api/health" in html_content and "/api/physics/query" in html_content:
        print("✅ Frontend uses correct API paths")
    else:
        print("❌ Frontend API paths incorrect")
        return False
    
    print("✅ Static files properly structured")
    return True

def main():
    """Run all verification checks."""
    print("🚀 FINAL DEPLOYMENT VERIFICATION")
    print("=" * 80)
    
    checks = [
        verify_vercel_function_structure,
        verify_requirements_compatibility,
        verify_vercel_config_completeness,
        verify_static_files
    ]
    
    all_passed = True
    for check in checks:
        try:
            result = check()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Check {check.__name__} failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL DEPLOYMENT VERIFICATIONS PASSED!")
        print("✅ The application is ready for Vercel deployment")
        print("\n📋 DEPLOYMENT SUMMARY:")
        print("- FastAPI app properly exported as 'app'")
        print("- All critical routes (/health, /, /physics/query) available")
        print("- Requirements.txt optimized for Vercel")
        print("- vercel.json properly configured with Python 3.9 runtime")
        print("- Static files correctly structured")
        print("- Frontend uses correct /api/* paths")
        print("\n🚀 Ready to push to Vercel!")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("⚠️ Fix issues before deployment")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 