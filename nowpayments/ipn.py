"""
IPN (Instant Payment Notification) signature verification.
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional


class IPNVerifier:
    """Verifies IPN signatures from NOWPayments."""
    
    def __init__(self, ipn_secret: str):
        """
        Initialize the IPN verifier.
        
        Args:
            ipn_secret: Your IPN secret key from NOWPayments dashboard
        """
        self.ipn_secret = ipn_secret.encode('utf-8')
    
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verify the IPN signature.
        
        Args:
            data: The JSON payload from the IPN request
            signature: The X-NOWPAYMENTS-Sig header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Sort the keys to ensure consistent ordering
            sorted_data = dict(sorted(data.items()))
            
            # Convert to JSON string
            json_string = json.dumps(sorted_data, separators=(',', ':'))
            
            # Create HMAC-SHA512 signature
            expected_signature = hmac.new(
                self.ipn_secret,
                json_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception:
            return False
    
    def verify_request(self, request_data: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """
        Verify an IPN request from headers and body.
        
        Args:
            request_data: The request body (JSON data)
            headers: The request headers
            
        Returns:
            True if the request is valid, False otherwise
        """
        signature = headers.get('X-NOWPAYMENTS-Sig')
        if not signature:
            return False
            
        return self.verify_signature(request_data, signature) 