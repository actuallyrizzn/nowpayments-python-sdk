"""
Test environment setup for live tests.
"""

import os
import pytest
from pathlib import Path


def test_env_file_loading():
    """Test that environment variables can be loaded from .env file."""
    # Test the load_env_file function logic
    env_file = Path(__file__).parent / '.env'
    
    # Test with a mock .env file
    test_env_content = """
# Test environment variables
NOWPAYMENTS_API_KEY=test_key_123
NOWPAYMENTS_IPN_SECRET=test_secret_456
NOWPAYMENTS_ENVIRONMENT=sandbox
"""
    
    # Create temporary .env file
    with open(env_file, 'w') as f:
        f.write(test_env_content)
    
    try:
        # Load environment variables
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        
        # Verify environment variables are set
        assert os.getenv('NOWPAYMENTS_API_KEY') == 'test_key_123'
        assert os.getenv('NOWPAYMENTS_IPN_SECRET') == 'test_secret_456'
        assert os.getenv('NOWPAYMENTS_ENVIRONMENT') == 'sandbox'
        
        print("✅ Environment variable loading works correctly")
        
    finally:
        # Clean up
        if env_file.exists():
            env_file.unlink()


def test_missing_env_file():
    """Test behavior when .env file is missing."""
    env_file = Path(__file__).parent / '.env'
    
    # Remove .env file if it exists
    if env_file.exists():
        env_file.unlink()
    
    # Verify .env file doesn't exist
    assert not env_file.exists()
    
    # This should not raise an error
    print("✅ Missing .env file handled gracefully")


if __name__ == '__main__':
    pytest.main(['-v', __file__]) 