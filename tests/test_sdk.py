"""
Basic tests for the NOWPayments Python SDK.
"""

import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime

from nowpayments import NOWPayments, IPNVerifier
from nowpayments.exceptions import NOWPaymentsError, AuthenticationError
from nowpayments.models import Payment, Estimate, Currency


class TestNOWPaymentsClient(unittest.TestCase):
    """Test the NOWPayments client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = NOWPayments(
            api_key="test_api_key",
            sandbox=True
        )
    
    def test_client_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, "test_api_key")
        self.assertTrue(self.client.sandbox)
        self.assertEqual(self.client.base_url, "https://api-sandbox.nowpayments.io/v1")
    
    def test_parse_decimal(self):
        """Test decimal parsing."""
        self.assertEqual(self.client._parse_decimal("123.45"), Decimal("123.45"))
        self.assertEqual(self.client._parse_decimal(123.45), Decimal("123.45"))
        self.assertIsNone(self.client._parse_decimal(None))
        self.assertIsNone(self.client._parse_decimal("invalid"))
    
    def test_parse_datetime(self):
        """Test datetime parsing."""
        dt_str = "2023-01-01T12:00:00Z"
        parsed = self.client._parse_datetime(dt_str)
        self.assertIsInstance(parsed, datetime)
        self.assertEqual(parsed.year, 2023)
        self.assertEqual(parsed.month, 1)
        self.assertEqual(parsed.day, 1)
        
        self.assertIsNone(self.client._parse_datetime(None))
        self.assertIsNone(self.client._parse_datetime("invalid"))
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_status(self, mock_request):
        """Test get_status method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "OK"}
        mock_request.return_value = mock_response
        
        result = self.client.get_status()
        
        self.assertEqual(result, {"message": "OK"})
        mock_request.assert_called_once()
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_currencies(self, mock_request):
        """Test get_currencies method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"currencies": ["btc", "eth", "ltc"]}
        mock_request.return_value = mock_response
        
        result = self.client.get_currencies()
        
        self.assertEqual(result, ["btc", "eth", "ltc"])
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_estimate(self, mock_request):
        """Test get_estimate method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount_from": 100.0,
            "currency_from": "usd",
            "currency_to": "btc",
            "estimated_amount": 0.0045
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_estimate(100.0, "usd", "btc")
        
        self.assertIsInstance(result, Estimate)
        self.assertEqual(result.amount_from, Decimal("100.0"))
        self.assertEqual(result.currency_from, "usd")
        self.assertEqual(result.currency_to, "btc")
        self.assertEqual(result.estimated_amount, Decimal("0.0045"))
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_payment(self, mock_request):
        """Test create_payment method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payment_id": 123456789,
            "payment_status": "waiting",
            "pay_address": "test_address",
            "price_amount": 50.0,
            "price_currency": "usd",
            "pay_amount": 0.002,
            "pay_currency": "btc",
            "order_id": "test_order",
            "created_at": "2023-01-01T12:00:00Z"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_payment(
            price_amount=50.0,
            price_currency="usd",
            pay_currency="btc",
            order_id="test_order"
        )
        
        self.assertIsInstance(result, Payment)
        self.assertEqual(result.payment_id, 123456789)
        self.assertEqual(result.payment_status, "waiting")
        self.assertEqual(result.pay_address, "test_address")
        self.assertEqual(result.price_amount, Decimal("50.0"))
        self.assertEqual(result.pay_amount, Decimal("0.002"))
    
    @patch('nowpayments.client.requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(AuthenticationError):
            self.client.get_status()
    
    @patch('nowpayments.client.requests.Session.request')
    def test_general_error(self, mock_request):
        """Test general error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(NOWPaymentsError):
            self.client.get_status()


class TestIPNVerifier(unittest.TestCase):
    """Test the IPN verifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.verifier = IPNVerifier(ipn_secret="test_secret")
    
    def test_verifier_initialization(self):
        """Test IPN verifier initialization."""
        self.assertEqual(self.verifier.ipn_secret, b"test_secret")
    
    def test_verify_signature(self):
        """Test signature verification."""
        # This is a simplified test - in practice, you'd need real signatures
        data = {"test": "data"}
        signature = "invalid_signature"
        
        result = self.verifier.verify_signature(data, signature)
        self.assertFalse(result)
    
    def test_verify_request(self):
        """Test request verification."""
        data = {"test": "data"}
        headers = {"X-NOWPAYMENTS-Sig": "test_signature"}
        
        result = self.verifier.verify_request(data, headers)
        self.assertFalse(result)
        
        # Test with missing signature
        headers_no_sig = {}
        result = self.verifier.verify_request(data, headers_no_sig)
        self.assertFalse(result)


class TestModels(unittest.TestCase):
    """Test the data models."""
    
    def test_payment_model(self):
        """Test Payment model."""
        payment = Payment(
            payment_id=123456789,
            payment_status="waiting",
            pay_address="test_address",
            price_amount=Decimal("50.0"),
            price_currency="usd",
            pay_amount=Decimal("0.002"),
            pay_currency="btc"
        )
        
        self.assertEqual(payment.payment_id, 123456789)
        self.assertEqual(payment.payment_status, "waiting")
        self.assertEqual(payment.pay_address, "test_address")
        self.assertEqual(payment.price_amount, Decimal("50.0"))
        self.assertEqual(payment.pay_currency, "btc")
    
    def test_currency_model(self):
        """Test Currency model."""
        currency = Currency(
            currency="btc",
            name="Bitcoin",
            min_amount=Decimal("0.0001"),
            enabled=True,
            networks=["BTC"]
        )
        
        self.assertEqual(currency.currency, "btc")
        self.assertEqual(currency.name, "Bitcoin")
        self.assertEqual(currency.min_amount, Decimal("0.0001"))
        self.assertTrue(currency.enabled)
        self.assertEqual(currency.networks, ["BTC"])
    
    def test_estimate_model(self):
        """Test Estimate model."""
        estimate = Estimate(
            amount_from=Decimal("100.0"),
            currency_from="usd",
            currency_to="btc",
            estimated_amount=Decimal("0.0045")
        )
        
        self.assertEqual(estimate.amount_from, Decimal("100.0"))
        self.assertEqual(estimate.currency_from, "usd")
        self.assertEqual(estimate.currency_to, "btc")
        self.assertEqual(estimate.estimated_amount, Decimal("0.0045"))


if __name__ == "__main__":
    unittest.main() 