#!/usr/bin/env python3
"""
Validation script to check test files and configuration before pushing to GitLab.
This script validates:
1. Python syntax in test files
2. YAML syntax in Kubernetes manifests
3. Test discovery with pytest
4. Import validation
"""

import sys
import os
import ast
import subprocess
import yaml
from pathlib import Path

def check_python_syntax(file_path):
    """Check Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_yaml_syntax(file_path):
    """Check YAML file syntax (supports multi-document YAML)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try to load all documents (for Kubernetes multi-doc YAML)
            try:
                list(yaml.safe_load_all(content))
            except yaml.YAMLError:
                # Fallback to single document
                yaml.safe_load(content)
        return True, None
    except yaml.YAMLError as e:
        return False, f"YAML error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_imports():
    """Check if required packages can be imported"""
    required_packages = {
        'pytest': 'pytest',
        'pymysql': 'pymysql',
        'requests': 'requests',
        'elasticsearch': 'elasticsearch',
        'yaml': 'pyyaml'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    return missing

def discover_tests():
    """Check if pytest can discover tests"""
    try:
        result = subprocess.run(
            ['pytest', '--collect-only', '-q', 'tests/'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "pytest not found. Install with: pip install -r requirements.txt"
    except subprocess.TimeoutExpired:
        return False, "pytest collection timed out"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main validation function"""
    print("=" * 60)
    print("Pre-Push Validation Script")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Check Python test files
    print("\n[1/5] Checking Python test files...")
    test_files = [
        'tests/__init__.py',
        'tests/test_mysql.py',
        'tests/test_elasticsearch.py',
        'tests/test_nginx.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            valid, error = check_python_syntax(test_file)
            if valid:
                print(f"  ✓ {test_file}")
            else:
                print(f"  ✗ {test_file}: {error}")
                errors.append(f"{test_file}: {error}")
        else:
            print(f"  ✗ {test_file}: File not found")
            errors.append(f"{test_file}: File not found")
    
    # Check YAML files
    print("\n[2/5] Checking YAML files...")
    yaml_files = [
        '.gitlab-ci.yml',
        'deployments/mysql-deployment.yaml',
        'deployments/elasticsearch-deployment.yaml',
        'deployments/nginx-deployment.yaml'
    ]
    
    for yaml_file in yaml_files:
        if os.path.exists(yaml_file):
            valid, error = check_yaml_syntax(yaml_file)
            if valid:
                print(f"  ✓ {yaml_file}")
            else:
                print(f"  ✗ {yaml_file}: {error}")
                errors.append(f"{yaml_file}: {error}")
        else:
            print(f"  ✗ {yaml_file}: File not found")
            errors.append(f"{yaml_file}: File not found")
    
    # Check Dockerfile
    print("\n[3/5] Checking Dockerfile...")
    if os.path.exists('Dockerfile'):
        print("  ✓ Dockerfile exists")
    else:
        print("  ✗ Dockerfile not found")
        errors.append("Dockerfile: File not found")
    
    # Check requirements.txt
    print("\n[4/5] Checking requirements.txt...")
    if os.path.exists('requirements.txt'):
        print("  ✓ requirements.txt exists")
        with open('requirements.txt', 'r') as f:
            deps = f.read().strip()
            if deps:
                print(f"  ✓ Contains {len(deps.splitlines())} dependencies")
            else:
                warnings.append("requirements.txt is empty")
    else:
        print("  ✗ requirements.txt not found")
        errors.append("requirements.txt: File not found")
    
    # Check imports (optional - just warn if missing)
    print("\n[5/5] Checking Python package imports...")
    missing_packages = check_imports()
    if missing_packages:
        print(f"  ⚠ Missing packages: {', '.join(missing_packages)}")
        print(f"    Install with: pip install {' '.join(missing_packages)}")
        warnings.append(f"Missing packages: {', '.join(missing_packages)}")
    else:
        print("  ✓ All required packages are available")
    
    # Try to discover tests with pytest
    print("\n[6/6] Checking pytest test discovery...")
    test_discovery, output = discover_tests()
    if test_discovery:
        # Count tests
        test_count = output.count('::test_')
        print(f"  ✓ pytest can discover tests ({test_count} test functions found)")
        print(f"    Output: {output[:200]}...")
    else:
        print(f"  ⚠ pytest test discovery failed: {output[:200]}")
        warnings.append(f"pytest discovery: {output[:200]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    if errors:
        print(f"\n✗ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        print("\n❌ Validation FAILED. Please fix errors before pushing.")
        return 1
    else:
        print("\n✓ No syntax errors found!")
    
    if warnings:
        print(f"\n⚠ WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
        print("\n⚠ Some warnings found, but code should work in CI/CD environment.")
    
    print("\n✅ Validation PASSED. Code is ready to push!")
    print("\nNote: Full integration tests require:")
    print("  - Kubernetes cluster with services deployed")
    print("  - Access to NodePort services")
    print("  - Proper KUBERNETES_NODE_IP environment variable")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

