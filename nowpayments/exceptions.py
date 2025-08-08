"""
Custom exceptions for the NOWPayments SDK.
"""

from typing import Optional, Dict, Any


class NOWPaymentsError(Exception):
    """Base exception for all NOWPayments SDK errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(NOWPaymentsError):
    """Raised when authentication fails (invalid API key, etc.)."""
    pass


class PaymentError(NOWPaymentsError):
    """Raised when payment-related operations fail."""
    pass


class PayoutError(NOWPaymentsError):
    """Raised when payout-related operations fail."""
    pass


class SubscriptionError(NOWPaymentsError):
    """Raised when subscription-related operations fail."""
    pass


class CustodyError(NOWPaymentsError):
    """Raised when custody/sub-account operations fail."""
    pass


class ConversionError(NOWPaymentsError):
    """Raised when currency conversion operations fail."""
    pass


class ValidationError(NOWPaymentsError):
    """Raised when input validation fails."""
    pass


class RateLimitError(NOWPaymentsError):
    """Raised when API rate limits are exceeded."""
    pass


class IPNError(NOWPaymentsError):
    """Raised when IPN signature verification fails."""
    pass 