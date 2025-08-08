#!/usr/bin/env python3
"""
Live Test Runner for NOWPayments Python SDK

This script runs live tests against the actual NOWPayments API.
Use with caution as these tests make real API calls.

Usage:
    python run_live_tests.py [--api-key YOUR_API_KEY] [--sandbox] [--production]
"""

import os
import sys
import argparse
import warnings
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def load_env_file():
    """Load environment variables from .env file in tests directory."""
    env_file = Path(__file__).parent / 'tests' / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment variables from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
        print("   Copy tests/env.example to tests/.env and fill in your credentials")

def main():
    """Run live tests with proper configuration."""
    parser = argparse.ArgumentParser(description='Run live tests for NOWPayments SDK')
    parser.add_argument('--api-key', help='NOWPayments API key')
    parser.add_argument('--sandbox', action='store_true', default=True, 
                       help='Use sandbox environment (default)')
    parser.add_argument('--production', action='store_true', 
                       help='Use production environment (use with caution)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--test', help='Run specific test (e.g., test_live_api_status)')
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_env_file()
    
    # Set environment variables from command line (overrides .env)
    if args.api_key:
        os.environ['NOWPAYMENTS_API_KEY'] = args.api_key
    
    # Environment warning
    environment = os.getenv('NOWPAYMENTS_ENVIRONMENT', 'sandbox').lower()
    if args.production or environment == 'production':
        print("⚠️  WARNING: Running live tests against PRODUCTION environment!")
        print("   This will make real API calls that may affect your account.")
        response = input("   Are you sure you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            return
        os.environ['NOWPAYMENTS_ENVIRONMENT'] = 'production'
    else:
        print("✅ Using SANDBOX environment for live tests")
        os.environ['NOWPAYMENTS_ENVIRONMENT'] = 'sandbox'
    
    # Import and run tests
    try:
        import pytest
        
        # Build pytest arguments
        pytest_args = ['-v', 'tests/test_live.py']
        
        if args.verbose:
            pytest_args.append('-s')  # Show print statements
        
        if args.test:
            pytest_args.append(f'-k {args.test}')
        
        # Environment is already set above
        
        print(f"🚀 Running live tests with args: {' '.join(pytest_args)}")
        print("📋 This may take a few minutes...")
        
        # Run the tests
        exit_code = pytest.main(pytest_args)
        
        if exit_code == 0:
            print("✅ All live tests passed!")
        else:
            print(f"❌ Some live tests failed (exit code: {exit_code})")
        
        return exit_code
        
    except ImportError as e:
        print(f"❌ Error importing pytest: {e}")
        print("💡 Make sure you have installed development dependencies:")
        print("   pip install -r requirements-dev.txt")
        return 1
    except Exception as e:
        print(f"❌ Error running live tests: {e}")
        return 1

if __name__ == '__main__':
    # Suppress warnings for cleaner output
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    exit_code = main()
    sys.exit(exit_code) 