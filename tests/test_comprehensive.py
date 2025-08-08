"""
Comprehensive tests for the NOWPayments Python SDK to achieve 100% coverage.
"""

import unittest
import requests
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime

from nowpayments import NOWPayments, IPNVerifier
from nowpayments.exceptions import (
    NOWPaymentsError, AuthenticationError, PaymentError, PayoutError,
    SubscriptionError, CustodyError, ConversionError, ValidationError, RateLimitError
)
from nowpayments.models import (
    Payment, PaymentStatus, Invoice, Subscription, SubscriptionPlan,
    PayoutBatch, PayoutWithdrawal, UserAccount, Transfer, Conversion,
    Currency, Estimate, AddressValidation
)


class TestNOWPaymentsClientComprehensive(unittest.TestCase):
    """Comprehensive tests for the NOWPayments client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = NOWPayments(
            api_key="test_api_key",
            sandbox=True
        )
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful request handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        result = self.client._make_request("GET", "/test")
        self.assertEqual(result, {"success": True})
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(AuthenticationError):
            self.client._make_request("GET", "/test")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Rate limit exceeded"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(RateLimitError):
            self.client._make_request("GET", "/test")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_payment_error(self, mock_request):
        """Test payment error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Payment error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(PaymentError):
            self.client._make_request("POST", "/payment")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_payout_error(self, mock_request):
        """Test payout error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Payout error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(PayoutError):
            self.client._make_request("POST", "/payout")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_subscription_error(self, mock_request):
        """Test subscription error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Subscription error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(SubscriptionError):
            self.client._make_request("POST", "/subscription")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_custody_error(self, mock_request):
        """Test custody error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Custody error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(CustodyError):
            self.client._make_request("POST", "/custody")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_conversion_error(self, mock_request):
        """Test conversion error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Conversion error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(ConversionError):
            self.client._make_request("POST", "/conversion")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_validation_error(self, mock_request):
        """Test validation error handling."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Validation error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(ValidationError):
            self.client._make_request("POST", "/validate")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_general_error(self, mock_request):
        """Test general error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(NOWPaymentsError):
            self.client._make_request("GET", "/test")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_retry_success(self, mock_request):
        """Test retry logic with eventual success."""
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.json.return_value = {"message": "Server error"}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        mock_request.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        result = self.client._make_request("GET", "/test")
        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_request.call_count, 3)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_make_request_retry_failure(self, mock_request):
        """Test retry logic with eventual failure."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Server error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(NOWPaymentsError):
            self.client._make_request("GET", "/test")
        
        # Should have retried 4 times (initial + 3 retries)
        self.assertEqual(mock_request.call_count, 4)
    
    def test_parse_datetime_valid(self):
        """Test datetime parsing with valid input."""
        dt_str = "2023-01-01T12:00:00Z"
        parsed = self.client._parse_datetime(dt_str)
        self.assertIsInstance(parsed, datetime)
        self.assertEqual(parsed.year, 2023)
        self.assertEqual(parsed.month, 1)
        self.assertEqual(parsed.day, 1)
    
    def test_parse_datetime_invalid(self):
        """Test datetime parsing with invalid input."""
        self.assertIsNone(self.client._parse_datetime(None))
        self.assertIsNone(self.client._parse_datetime("invalid"))
    
    def test_parse_decimal_valid(self):
        """Test decimal parsing with valid input."""
        self.assertEqual(self.client._parse_decimal("123.45"), Decimal("123.45"))
        self.assertEqual(self.client._parse_decimal(123.45), Decimal("123.45"))
        self.assertEqual(self.client._parse_decimal(123), Decimal("123"))
    
    def test_parse_decimal_invalid(self):
        """Test decimal parsing with invalid input."""
        self.assertIsNone(self.client._parse_decimal(None))
        self.assertIsNone(self.client._parse_decimal("invalid"))
        self.assertIsNone(self.client._parse_decimal("abc"))
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_merchant_currencies(self, mock_request):
        """Test get_merchant_currencies method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"currencies": ["btc", "eth"]}
        mock_request.return_value = mock_response
        
        result = self.client.get_merchant_currencies()
        self.assertEqual(result, ["btc", "eth"])
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_full_currencies(self, mock_request):
        """Test get_full_currencies method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "currencies": [
                {
                    "currency": "btc",
                    "name": "Bitcoin",
                    "min_amount": "0.0001",
                    "enabled": True,
                    "networks": ["BTC"]
                }
            ]
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_full_currencies()
        self.assertIsInstance(result[0], Currency)
        self.assertEqual(result[0].currency, "btc")
        self.assertEqual(result[0].name, "Bitcoin")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_min_amount(self, mock_request):
        """Test get_min_amount method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "min_amount": "0.0001",
            "currency_from": "usd",
            "currency_to": "btc"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_min_amount("usd", "btc")
        self.assertEqual(result["min_amount"], "0.0001")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_payment_status(self, mock_request):
        """Test get_payment_status method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payment_id": 123456789,
            "payment_status": "confirmed",
            "pay_address": "test_address",
            "price_amount": 50.0,
            "price_currency": "usd",
            "pay_amount": 0.002,
            "pay_currency": "btc",
            "order_id": "test_order",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:30:00Z",
            "purchase_id": "test_purchase",
            "outcome_amount": 0.002,
            "outcome_currency": "btc"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_payment_status(123456789)
        self.assertIsInstance(result, PaymentStatus)
        self.assertEqual(result.payment_id, 123456789)
        self.assertEqual(result.payment_status, "confirmed")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_payments(self, mock_request):
        """Test list_payments method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payments": [
                {
                    "payment_id": 123456789,
                    "payment_status": "waiting",
                    "pay_address": "test_address",
                    "price_amount": 50.0,
                    "price_currency": "usd",
                    "pay_amount": 0.002,
                    "pay_currency": "btc"
                }
            ],
            "total": 1,
            "page": 1,
            "limit": 10
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_payments(limit=10, page=1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["payments"]), 1)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_update_payment_estimate(self, mock_request):
        """Test update_payment_estimate method."""
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
            "pay_amount_updated": 0.0021
        }
        mock_request.return_value = mock_response
        
        result = self.client.update_payment_estimate(123456789)
        self.assertIsInstance(result, Payment)
        self.assertEqual(result.payment_id, 123456789)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_invoice(self, mock_request):
        """Test create_invoice method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "invoice_id": "test_invoice_id",
            "invoice_url": "https://nowpayments.io/invoice/test",
            "price_amount": 50.0,
            "price_currency": "usd",
            "order_id": "test_order",
            "order_description": "Test order",
            "ipn_callback_url": "https://example.com/callback",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_invoice(
            price_amount=50.0,
            price_currency="usd",
            order_id="test_order",
            order_description="Test order"
        )
        self.assertIsInstance(result, Invoice)
        self.assertEqual(result.invoice_id, "test_invoice_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_invoice_status(self, mock_request):
        """Test get_invoice_status method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "invoice_id": "test_invoice_id",
            "invoice_url": "https://nowpayments.io/invoice/test",
            "price_amount": 50.0,
            "price_currency": "usd",
            "order_id": "test_order",
            "status": "active"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_invoice_status("test_invoice_id")
        self.assertIsInstance(result, Invoice)
        self.assertEqual(result.invoice_id, "test_invoice_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_invoice_payment(self, mock_request):
        """Test create_invoice_payment method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payment_id": 123456789,
            "payment_status": "waiting",
            "pay_address": "test_address",
            "price_amount": 50.0,
            "price_currency": "usd",
            "pay_amount": 0.002,
            "pay_currency": "btc"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_invoice_payment(
            invoice_id="test_invoice_id",
            pay_currency="btc"
        )
        self.assertIsInstance(result, Payment)
        self.assertEqual(result.payment_id, 123456789)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_subscription_plan(self, mock_request):
        """Test create_subscription_plan method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "plan_id": "test_plan_id",
            "title": "Test Plan",
            "interval_day": 30,
            "amount": 50.0,
            "currency": "usd",
            "ipn_callback_url": "https://example.com/callback",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_subscription_plan(
            title="Test Plan",
            interval_day=30,
            amount=50.0,
            currency="usd"
        )
        self.assertIsInstance(result, SubscriptionPlan)
        self.assertEqual(result.id, "test_plan_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_update_subscription_plan(self, mock_request):
        """Test update_subscription_plan method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "plan_id": "test_plan_id",
            "title": "Updated Plan",
            "interval_day": 30,
            "amount": 60.0,
            "currency": "usd"
        }
        mock_request.return_value = mock_response
        
        result = self.client.update_subscription_plan(
            plan_id="test_plan_id",
            title="Updated Plan",
            amount=60.0
        )
        self.assertIsInstance(result, SubscriptionPlan)
        self.assertEqual(result.title, "Updated Plan")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_subscription_plan(self, mock_request):
        """Test get_subscription_plan method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "plan_id": "test_plan_id",
            "title": "Test Plan",
            "interval_day": 30,
            "amount": 50.0,
            "currency": "usd"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_subscription_plan("test_plan_id")
        self.assertIsInstance(result, SubscriptionPlan)
        self.assertEqual(result.id, "test_plan_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_subscription_plans(self, mock_request):
        """Test list_subscription_plans method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "plans": [
                {
                    "plan_id": "test_plan_id",
                    "title": "Test Plan",
                    "interval_day": 30,
                    "amount": 50.0,
                    "currency": "usd"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_subscription_plans()
        self.assertIsInstance(result[0], SubscriptionPlan)
        self.assertEqual(result[0].id, "test_plan_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_subscription(self, mock_request):
        """Test create_subscription method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subscription_id": "test_subscription_id",
            "plan_id": "test_plan_id",
            "email": "test@example.com",
            "status": "active",
            "order_id": "test_order",
            "order_description": "Test subscription"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_subscription(
            plan_id="test_plan_id",
            email="test@example.com",
            order_id="test_order"
        )
        self.assertIsInstance(result, Subscription)
        self.assertEqual(result.subscription_id, "test_subscription_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_subscriptions(self, mock_request):
        """Test list_subscriptions method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subscriptions": [
                {
                    "subscription_id": "test_subscription_id",
                    "plan_id": "test_plan_id",
                    "email": "test@example.com",
                    "status": "active"
                }
            ],
            "total": 1,
            "page": 1,
            "limit": 10
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_subscriptions(limit=10, page=1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["subscriptions"]), 1)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_subscription(self, mock_request):
        """Test get_subscription method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subscription_id": "test_subscription_id",
            "plan_id": "test_plan_id",
            "email": "test@example.com",
            "status": "active"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_subscription("test_subscription_id")
        self.assertIsInstance(result, Subscription)
        self.assertEqual(result.subscription_id, "test_subscription_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_delete_subscription(self, mock_request):
        """Test delete_subscription method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Subscription deleted"}
        mock_request.return_value = mock_response
        
        result = self.client.delete_subscription("test_subscription_id")
        self.assertTrue(result)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_payout(self, mock_request):
        """Test create_payout method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "batch_id": "test_batch_id",
            "withdrawals": [
                {
                    "withdrawal_id": "test_withdrawal_id",
                    "address": "test_address",
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "pending"
                }
            ],
            "status": "pending"
        }
        mock_request.return_value = mock_response
        
        withdrawals = [
            {
                "address": "test_address",
                "currency": "btc",
                "amount": 0.001
            }
        ]
        
        result = self.client.create_payout(withdrawals=withdrawals)
        self.assertIsInstance(result, PayoutBatch)
        self.assertEqual(result.batch_id, "test_batch_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_verify_payout(self, mock_request):
        """Test verify_payout method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "batch_id": "test_batch_id",
            "withdrawals": [
                {
                    "withdrawal_id": "test_withdrawal_id",
                    "address": "test_address",
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "confirmed"
                }
            ],
            "status": "confirmed"
        }
        mock_request.return_value = mock_response
        
        result = self.client.verify_payout(
            batch_id="test_batch_id",
            code="123456"
        )
        self.assertIsInstance(result, PayoutBatch)
        self.assertEqual(result.batch_id, "test_batch_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_payout_status(self, mock_request):
        """Test get_payout_status method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "batch_id": "test_batch_id",
            "withdrawals": [
                {
                    "withdrawal_id": "test_withdrawal_id",
                    "address": "test_address",
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "confirmed"
                }
            ],
            "status": "confirmed"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_payout_status("test_batch_id")
        self.assertIsInstance(result, PayoutBatch)
        self.assertEqual(result.batch_id, "test_batch_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_payouts(self, mock_request):
        """Test list_payouts method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payouts": [
                {
                    "batch_id": "test_batch_id",
                    "status": "confirmed"
                }
            ],
            "total": 1,
            "page": 1,
            "limit": 10
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_payouts(limit=10, page=1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["payouts"]), 1)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_validate_address(self, mock_request):
        """Test validate_address method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "address": "test_address",
            "currency": "btc",
            "result": True,
            "message": "Valid address"
        }
        mock_request.return_value = mock_response
        
        result = self.client.validate_address(
            address="test_address",
            currency="btc"
        )
        self.assertIsInstance(result, AddressValidation)
        self.assertEqual(result.address, "test_address")
        self.assertTrue(result.result)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_user_account(self, mock_request):
        """Test create_user_account method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": 123,
            "external_id": "test_external_id",
            "email": "test@example.com",
            "balance": {
                "btc": 0.0,
                "eth": 0.0
            }
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_user_account(
            external_id="test_external_id",
            email="test@example.com"
        )
        self.assertIsInstance(result, UserAccount)
        self.assertEqual(result.user_id, 123)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_user_balance(self, mock_request):
        """Test get_user_balance method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": 123,
            "external_id": "test_external_id",
            "email": "test@example.com",
            "balance": {
                "btc": 0.001,
                "eth": 0.01
            }
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_user_balance(123)
        self.assertIsInstance(result, UserAccount)
        self.assertEqual(result.user_id, 123)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_user_accounts(self, mock_request):
        """Test list_user_accounts method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accounts": [
                {
                    "user_id": 123,
                    "external_id": "test_external_id",
                    "email": "test@example.com",
                    "balance": {
                        "btc": 0.001,
                        "eth": 0.01
                    }
                }
            ],
            "total": 1,
            "offset": 0,
            "limit": 10
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_user_accounts(limit=10, offset=0)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["accounts"]), 1)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_user_payment(self, mock_request):
        """Test create_user_payment method."""
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
            "user_id": 123
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_user_payment(
            user_id=123,
            currency="btc",
            amount=0.002
        )
        self.assertIsInstance(result, Payment)
        self.assertEqual(result.payment_id, 123456789)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_transfer_funds(self, mock_request):
        """Test transfer_funds method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transfer_id": "test_transfer_id",
            "from_id": 123,
            "to_id": 456,
            "currency": "btc",
            "amount": 0.001,
            "status": "confirmed"
        }
        mock_request.return_value = mock_response
        
        result = self.client.transfer_funds(
            from_id=123,
            to_id=456,
            currency="btc",
            amount=0.001
        )
        self.assertIsInstance(result, Transfer)
        self.assertEqual(result.transfer_id, "test_transfer_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_transfers(self, mock_request):
        """Test list_transfers method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transfers": [
                {
                    "transfer_id": "test_transfer_id",
                    "from_id": 123,
                    "to_id": 456,
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "confirmed"
                }
            ],
            "total": 1,
            "offset": 0,
            "limit": 10
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_transfers(limit=10, offset=0)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["transfers"]), 1)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_transfer(self, mock_request):
        """Test get_transfer method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transfer_id": "test_transfer_id",
            "from_id": 123,
            "to_id": 456,
            "currency": "btc",
            "amount": 0.001,
            "status": "confirmed"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_transfer("test_transfer_id")
        self.assertIsInstance(result, Transfer)
        self.assertEqual(result.transfer_id, "test_transfer_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_withdraw_funds(self, mock_request):
        """Test withdraw_funds method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "withdrawal_id": "test_withdrawal_id",
            "user_id": 123,
            "currency": "btc",
            "amount": 0.001,
            "address": "test_address",
            "status": "pending"
        }
        mock_request.return_value = mock_response
        
        result = self.client.withdraw_funds(
            user_id=123,
            currency="btc",
            amount=0.001,
            address="test_address"
        )
        self.assertEqual(result["withdrawal_id"], "test_withdrawal_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_create_conversion(self, mock_request):
        """Test create_conversion method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "conversion_id": "test_conversion_id",
            "from_currency": "usd",
            "to_currency": "btc",
            "amount": 100.0,
            "converted_amount": 0.0045,
            "status": "pending"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_conversion(
            from_currency="usd",
            to_currency="btc",
            amount=100.0
        )
        self.assertIsInstance(result, Conversion)
        self.assertEqual(result.conversion_id, "test_conversion_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_get_conversion_status(self, mock_request):
        """Test get_conversion_status method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "conversion_id": "test_conversion_id",
            "from_currency": "usd",
            "to_currency": "btc",
            "amount": 100.0,
            "converted_amount": 0.0045,
            "status": "confirmed"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_conversion_status("test_conversion_id")
        self.assertIsInstance(result, Conversion)
        self.assertEqual(result.conversion_id, "test_conversion_id")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_list_conversions(self, mock_request):
        """Test list_conversions method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "conversions": [
                {
                    "conversion_id": "test_conversion_id",
                    "from_currency": "usd",
                    "to_currency": "btc",
                    "amount": 100.0,
                    "converted_amount": 0.0045,
                    "status": "confirmed"
                }
            ],
            "total": 1,
            "offset": 0,
            "limit": 10
        }
        mock_request.return_value = mock_response
        
        result = self.client.list_conversions(limit=10, offset=0)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["conversions"]), 1)


class TestIPNVerifierComprehensive(unittest.TestCase):
    """Comprehensive tests for the IPN verifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.verifier = IPNVerifier(ipn_secret="test_secret")
    
    def test_verify_signature_with_valid_signature(self):
        """Test signature verification with a valid signature."""
        import hmac
        import hashlib
        import json
        
        data = {"test": "data", "amount": 100}
        sorted_data = dict(sorted(data.items()))
        json_string = json.dumps(sorted_data, separators=(',', ':'))
        expected_signature = hmac.new(
            b"test_secret",
            json_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        result = self.verifier.verify_signature(data, expected_signature)
        self.assertTrue(result)
    
    def test_verify_signature_with_invalid_signature(self):
        """Test signature verification with an invalid signature."""
        data = {"test": "data"}
        signature = "invalid_signature"
        
        result = self.verifier.verify_signature(data, signature)
        self.assertFalse(result)
    
    def test_verify_signature_with_exception(self):
        """Test signature verification when an exception occurs."""
        # This will cause an exception in the verification process
        result = self.verifier.verify_signature("invalid_data", "signature")
        self.assertFalse(result)
    
    def test_verify_request_with_signature(self):
        """Test request verification with signature header."""
        data = {"test": "data"}
        headers = {"X-NOWPAYMENTS-Sig": "test_signature"}
        
        result = self.verifier.verify_request(data, headers)
        self.assertFalse(result)  # Should be False because signature is invalid
    
    def test_verify_request_without_signature(self):
        """Test request verification without signature header."""
        data = {"test": "data"}
        headers = {}
        
        result = self.verifier.verify_request(data, headers)
        self.assertFalse(result)


class TestModelsComprehensive(unittest.TestCase):
    """Comprehensive tests for all data models."""
    
    def test_all_models_creation(self):
        """Test creation of all model instances."""
        # Test PaymentStatus
        payment_status = PaymentStatus(
            payment_id=123456789,
            payment_status="confirmed",
            pay_address="test_address",
            price_amount=Decimal("50.0"),
            price_currency="usd",
            pay_amount=Decimal("0.002"),
            pay_currency="btc",
            order_id="test_order",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            purchase_id="test_purchase",
            outcome_amount=Decimal("0.002"),
            outcome_currency="btc"
        )
        self.assertEqual(payment_status.payment_id, 123456789)
        
        # Test Invoice
        invoice = Invoice(
            invoice_id="test_invoice_id",
            invoice_url="https://nowpayments.io/invoice/test",
            price_amount=Decimal("50.0"),
            price_currency="usd",
            order_id="test_order",
            invoice_status="active"
        )
        self.assertEqual(invoice.invoice_id, "test_invoice_id")
        
        # Test SubscriptionPlan
        subscription_plan = SubscriptionPlan(
            id="test_plan_id",
            title="Test Plan",
            interval_day=30,
            amount=Decimal("50.0"),
            currency="usd",
            ipn_callback_url="https://example.com/callback",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        self.assertEqual(subscription_plan.id, "test_plan_id")
        
        # Test Subscription
        subscription = Subscription(
            subscription_id="test_subscription_id",
            plan_id="test_plan_id",
            email="test@example.com",
            status="active",
            order_id="test_order",
            order_description="Test subscription"
        )
        self.assertEqual(subscription.subscription_id, "test_subscription_id")
        
        # Test PayoutBatch
        payout_batch = PayoutBatch(
            batch_id="test_batch_id",
            withdrawals=[],
            status="pending"
        )
        self.assertEqual(payout_batch.batch_id, "test_batch_id")
        
        # Test PayoutWithdrawal
        payout_withdrawal = PayoutWithdrawal(
            id="test_withdrawal_id",
            address="test_address",
            currency="btc",
            amount=Decimal("0.001"),
            status="pending"
        )
        self.assertEqual(payout_withdrawal.id, "test_withdrawal_id")
        
        # Test UserAccount
        user_account = UserAccount(
            user_id=123,
            external_id="test_external_id",
            email="test@example.com",
            balance={"btc": Decimal("0.001"), "eth": Decimal("0.01")}
        )
        self.assertEqual(user_account.user_id, 123)
        
        # Test Transfer
        transfer = Transfer(
            transfer_id="test_transfer_id",
            from_id=123,
            to_id=456,
            currency="btc",
            amount=Decimal("0.001"),
            status="confirmed"
        )
        self.assertEqual(transfer.transfer_id, "test_transfer_id")
        
        # Test Conversion
        conversion = Conversion(
            conversion_id="test_conversion_id",
            from_currency="usd",
            to_currency="btc",
            from_amount=Decimal("100.0"),
            to_amount=Decimal("0.0045"),
            status="pending"
        )
        self.assertEqual(conversion.conversion_id, "test_conversion_id")
        
        # Test AddressValidation
        address_validation = AddressValidation(
            address="test_address",
            currency="btc",
            result=True,
            message="Valid address"
        )
        self.assertEqual(address_validation.address, "test_address")
        self.assertTrue(address_validation.result)

    def test_client_init_with_custom_base_url(self):
        """Test client initialization with custom base_url."""
        client = NOWPayments('test_key', base_url='https://custom.api.com/v1')
        assert client.base_url == 'https://custom.api.com/v1'
        assert not client.sandbox

    def test_make_request_with_custom_headers(self):
        """Test _make_request with custom headers."""
        client = NOWPayments('test_key')
        
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'test': 'data'}
            mock_response.content = b'{"test": "data"}'
            mock_request.return_value = mock_response
            
            result = client._make_request('GET', '/test', headers={'Custom-Header': 'value'})
            
            # Verify custom headers were merged
            call_args = mock_request.call_args
            assert 'Custom-Header' in call_args[1]['headers']
            assert call_args[1]['headers']['Custom-Header'] == 'value'
            assert result == {'test': 'data'}

    def test_make_request_retry_on_request_exception(self):
        """Test _make_request retry logic for RequestException."""
        client = NOWPayments('test_key', retries=2)
        
        with patch('requests.Session.request') as mock_request:
            # First two calls raise RequestException, third succeeds
            mock_request.side_effect = [
                requests.exceptions.RequestException("Connection error"),
                requests.exceptions.RequestException("Connection error"),
                Mock(status_code=200, json=lambda: {'success': True}, content=b'{"success": true}')
            ]
            
            result = client._make_request('GET', '/test')
            assert result == {'success': True}
            assert mock_request.call_count == 3

    def test_make_request_request_exception_failure(self):
        """Test _make_request when RequestException exhausts retries."""
        client = NOWPayments('test_key', retries=1)
        
        with patch('requests.Session.request') as mock_request:
            mock_request.side_effect = requests.exceptions.RequestException("Connection error")
            
            with self.assertRaises(NOWPaymentsError):
                client._make_request('GET', '/test')

    def test_create_payment_with_all_optional_params(self):
        """Test create_payment with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'payment_id': 123,
                'payment_status': 'waiting',
                'pay_address': 'test_address',
                'price_amount': '100.00',
                'price_currency': 'usd',
                'pay_amount': '0.001',
                'pay_currency': 'btc',
                'order_id': 'test_order',
                'order_description': 'Test payment',
                'ipn_callback_url': 'https://example.com/callback',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z',
                'purchase_id': 'test_purchase',
                'payout_address': 'payout_address',
                'payout_currency': 'btc',
                'external_id': 'ext_123'
            }
            
            result = client.create_payment(
                price_amount=100.0,
                price_currency='usd',
                pay_currency='btc',
                pay_amount=0.001,
                ipn_callback_url='https://example.com/callback',
                order_id='test_order',
                order_description='Test payment',
                purchase_id='test_purchase',
                payout_address='payout_address',
                payout_currency='btc',
                external_id='ext_123'
            )
            
            assert isinstance(result, Payment)
            assert result.payment_id == 123
            assert result.payment_status == 'waiting'
            assert result.pay_address == 'test_address'
            assert result.price_amount == Decimal('100.00')
            assert result.price_currency == 'usd'
            assert result.pay_amount == Decimal('0.001')
            assert result.pay_currency == 'btc'
            assert result.order_id == 'test_order'
            assert result.order_description == 'Test payment'
            assert result.ipn_callback_url == 'https://example.com/callback'
            assert result.purchase_id == 'test_purchase'
            assert result.payout_address == 'payout_address'
            assert result.payout_currency == 'btc'
            assert result.external_id == 'ext_123'

    def test_create_invoice_with_all_optional_params(self):
        """Test create_invoice with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'invoice_id': 'inv_123',
                'invoice_url': 'https://example.com/invoice',
                'invoice_status': 'new',
                'price_amount': '100.00',
                'price_currency': 'usd',
                'order_id': 'test_order',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_invoice(
                price_amount=100.0,
                price_currency='usd',
                order_id='test_order',
                order_description='Test invoice',
                ipn_callback_url='https://example.com/callback',
                success_url='https://example.com/success',
                cancel_url='https://example.com/cancel'
            )
            
            assert isinstance(result, Invoice)
            assert result.invoice_id == 'inv_123'
            assert result.invoice_url == 'https://example.com/invoice'
            assert result.invoice_status == 'new'
            assert result.price_amount == Decimal('100.00')
            assert result.price_currency == 'usd'
            assert result.order_id == 'test_order'

    def test_create_invoice_payment_with_all_optional_params(self):
        """Test create_invoice_payment with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'payment_id': 123,
                'payment_status': 'waiting',
                'pay_address': 'test_address',
                'price_amount': '100.00',
                'price_currency': 'usd',
                'pay_amount': '0.001',
                'pay_currency': 'btc',
                'order_id': 'test_order',
                'order_description': 'Test payment',
                'ipn_callback_url': 'https://example.com/callback',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z',
                'purchase_id': 'test_purchase',
                'payout_address': 'payout_address',
                'payout_currency': 'btc'
            }
            
            result = client.create_invoice_payment(
                invoice_id='inv_123',
                pay_currency='btc',
                purchase_id='test_purchase',
                order_description='Test payment',
                payout_address='payout_address',
                payout_currency='btc'
            )
            
            assert isinstance(result, Payment)
            assert result.payment_id == 123
            assert result.payment_status == 'waiting'
            assert result.pay_address == 'test_address'
            assert result.price_amount == Decimal('100.00')
            assert result.price_currency == 'usd'
            assert result.pay_amount == Decimal('0.001')
            assert result.pay_currency == 'btc'
            assert result.order_id == 'test_order'
            assert result.order_description == 'Test payment'
            assert result.ipn_callback_url == 'https://example.com/callback'
            assert result.purchase_id == 'test_purchase'
            assert result.payout_address == 'payout_address'
            assert result.payout_currency == 'btc'

    def test_create_invoice_payment_with_customer_email_and_payout_extra_id(self):
        """Test create_invoice_payment with customer_email and payout_extra_id parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'payment_id': 123,
                'payment_status': 'waiting',
                'pay_address': 'test_address',
                'price_amount': '100.00',
                'price_currency': 'usd',
                'pay_amount': '0.001',
                'pay_currency': 'btc',
                'order_id': 'test_order',
                'order_description': 'Test payment',
                'ipn_callback_url': 'https://example.com/callback',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z',
                'purchase_id': 'test_purchase',
                'payout_address': 'payout_address',
                'payout_currency': 'btc'
            }
            
            result = client.create_invoice_payment(
                invoice_id='inv_123',
                pay_currency='btc',
                purchase_id='test_purchase',
                order_description='Test payment',
                customer_email='test@example.com',
                payout_address='payout_address',
                payout_extra_id='extra_id',
                payout_currency='btc'
            )
            
            assert isinstance(result, Payment)
            assert result.payment_id == 123
            assert result.payment_status == 'waiting'
            assert result.pay_address == 'test_address'
            assert result.price_amount == Decimal('100.00')
            assert result.price_currency == 'usd'
            assert result.pay_amount == Decimal('0.001')
            assert result.pay_currency == 'btc'
            assert result.order_id == 'test_order'
            assert result.order_description == 'Test payment'
            assert result.ipn_callback_url == 'https://example.com/callback'
            assert result.purchase_id == 'test_purchase'
            assert result.payout_address == 'payout_address'
            assert result.payout_currency == 'btc'

    def test_create_subscription_plan_with_all_optional_params(self):
        """Test create_subscription_plan with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'id': 'plan_123',
                'title': 'Test Plan',
                'interval_day': 30,
                'amount': '100.00',
                'currency': 'usd',
                'ipn_callback_url': 'https://example.com/callback',
                'success_url': 'https://example.com/success',
                'cancel_url': 'https://example.com/cancel',
                'partially_paid_url': 'https://example.com/partial',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_subscription_plan(
                title='Test Plan',
                interval_day=30,
                amount=100.0,
                currency='usd',
                ipn_callback_url='https://example.com/callback',
                success_url='https://example.com/success',
                cancel_url='https://example.com/cancel',
                partially_paid_url='https://example.com/partial'
            )
            
            assert isinstance(result, SubscriptionPlan)
            assert result.id == 'plan_123'
            assert result.title == 'Test Plan'
            assert result.interval_day == 30
            assert result.amount == Decimal('100.00')
            assert result.currency == 'usd'
            assert result.ipn_callback_url == 'https://example.com/callback'
            assert result.success_url == 'https://example.com/success'
            assert result.cancel_url == 'https://example.com/cancel'
            assert result.partially_paid_url == 'https://example.com/partial'

    def test_create_subscription_with_all_optional_params(self):
        """Test create_subscription with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'subscription_id': 'sub_123',
                'plan_id': 'plan_123',
                'email': 'test@example.com',
                'status': 'active',
                'order_id': 'test_order',
                'order_description': 'Test subscription',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_subscription(
                plan_id='plan_123',
                email='test@example.com',
                order_id='test_order',
                order_description='Test subscription',
                starting_day=1
            )
            
            assert isinstance(result, Subscription)
            assert result.subscription_id == 'sub_123'
            assert result.plan_id == 'plan_123'
            assert result.email == 'test@example.com'
            assert result.status == 'active'
            assert result.order_id == 'test_order'
            assert result.order_description == 'Test subscription'

    def test_create_payout_with_all_optional_params(self):
        """Test create_payout with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'batch_id': 'batch_123',
                'withdrawals': [
                    {
                        'id': 'withdrawal_1',
                        'address': 'test_address',
                        'currency': 'btc',
                        'amount': '0.001',
                        'status': 'pending'
                    }
                ],
                'status': 'pending',
                'ipn_callback_url': 'https://example.com/callback',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_payout(
                withdrawals=[{
                    'address': 'test_address',
                    'currency': 'btc',
                    'amount': 0.001
                }],
                ipn_callback_url='https://example.com/callback',
                auth_token='test_token'
            )
            
            assert isinstance(result, PayoutBatch)
            assert result.batch_id == 'batch_123'
            assert result.status == 'pending'
            assert result.ipn_callback_url == 'https://example.com/callback'
            assert len(result.withdrawals) == 1
            assert result.withdrawals[0].id == 'withdrawal_1'
            assert result.withdrawals[0].address == 'test_address'
            assert result.withdrawals[0].currency == 'btc'
            assert result.withdrawals[0].amount == Decimal('0.001')
            assert result.withdrawals[0].status == 'pending'

    def test_create_user_account_with_all_optional_params(self):
        """Test create_user_account with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'user_id': 123,
                'external_id': 'ext_123',
                'email': 'test@example.com',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_user_account(
                external_id='ext_123',
                email='test@example.com'
            )
            
            assert isinstance(result, UserAccount)
            assert result.user_id == 123
            assert result.external_id == 'ext_123'
            assert result.email == 'test@example.com'

    def test_create_user_payment_with_all_optional_params(self):
        """Test create_user_payment with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'payment_id': 123,
                'status': 'waiting',
                'pay_address': 'test_address',
                'amount': '100.00',
                'currency': 'btc',
                'track_id': 'track_123',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_user_payment(
                user_id=123,
                currency='btc',
                amount=100.0,
                track_id='track_123'
            )
            
            assert isinstance(result, Payment)
            assert result.payment_id == 123
            assert result.payment_status == 'waiting'
            assert result.pay_address == 'test_address'
            assert result.price_amount == Decimal('100.00')
            assert result.price_currency == 'btc'
            assert result.pay_amount == Decimal('100.00')
            assert result.pay_currency == 'btc'
            assert result.order_id == 'track_123'

    def test_withdraw_funds_with_all_optional_params(self):
        """Test withdraw_funds with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'withdrawal_id': 'withdrawal_123',
                'user_id': 123,
                'currency': 'btc',
                'amount': '0.001',
                'address': 'withdrawal_address',
                'address_extra': 'extra_id',
                'status': 'pending',
                'ipn_callback_url': 'https://example.com/callback',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.withdraw_funds(
                user_id=123,
                currency='btc',
                amount=0.001,
                address='withdrawal_address',
                address_extra='extra_id',
                ipn_callback_url='https://example.com/callback'
            )
            
            assert isinstance(result, dict)
            assert result['withdrawal_id'] == 'withdrawal_123'
            assert result['user_id'] == 123
            assert result['currency'] == 'btc'
            assert result['amount'] == '0.001'
            assert result['address'] == 'withdrawal_address'
            assert result['address_extra'] == 'extra_id'
            assert result['status'] == 'pending'
            assert result['ipn_callback_url'] == 'https://example.com/callback'

    def test_create_conversion_with_all_optional_params(self):
        """Test create_conversion with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'conversion_id': 'conv_123',
                'from_currency': 'usd',
                'to_currency': 'btc',
                'from_amount': '100.00',
                'to_amount': '0.001',
                'status': 'pending',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            result = client.create_conversion(
                from_currency='usd',
                to_currency='btc',
                amount=100.0
            )
            
            assert isinstance(result, Conversion)
            assert result.conversion_id == 'conv_123'
            assert result.from_currency == 'usd'
            assert result.to_currency == 'btc'
            assert result.from_amount == Decimal('100.00')
            assert result.to_amount == Decimal('0.001')
            assert result.status == 'pending'

    def test_list_payments_with_all_optional_params(self):
        """Test list_payments with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'payments': [
                    {
                        'payment_id': 123,
                        'payment_status': 'waiting',
                        'pay_address': 'test_address',
                        'price_amount': '100.00',
                        'price_currency': 'usd',
                        'pay_amount': '0.001',
                        'pay_currency': 'btc'
                    }
                ],
                'total': 1,
                'page': 1,
                'limit': 10
            }
            
            result = client.list_payments(
                limit=10,
                page=1,
                order_by='created_at',
                order='desc',
                date_from='2023-01-01',
                date_to='2023-12-31',
                payment_status='waiting',
                pay_currency='btc'
            )
            
            assert isinstance(result, dict)
            assert 'payments' in result
            assert len(result['payments']) == 1
            assert result['total'] == 1
            assert result['page'] == 1
            assert result['limit'] == 10

    def test_list_subscriptions_with_all_optional_params(self):
        """Test list_subscriptions with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'subscriptions': [
                    {
                        'subscription_id': 'sub_123',
                        'plan_id': 'plan_123',
                        'email': 'test@example.com',
                        'status': 'active'
                    }
                ],
                'total': 1,
                'page': 1,
                'limit': 10
            }
            
            result = client.list_subscriptions(
                plan_id='plan_123',
                status='active',
                limit=10,
                page=1
            )
            
            assert isinstance(result, dict)
            assert 'subscriptions' in result
            assert len(result['subscriptions']) == 1
            assert result['total'] == 1
            assert result['page'] == 1
            assert result['limit'] == 10

    def test_list_payouts_with_all_optional_params(self):
        """Test list_payouts with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'payouts': [
                    {
                        'batch_id': 'batch_123',
                        'status': 'pending',
                        'total_amount': '0.001',
                        'total_currency': 'btc'
                    }
                ],
                'total': 1,
                'page': 1,
                'limit': 10
            }
            
            result = client.list_payouts(
                batch_id='batch_123',
                status='pending',
                date_from='2023-01-01',
                date_to='2023-12-31',
                order_by='created_at',
                order='desc',
                limit=10,
                page=1
            )
            
            assert isinstance(result, dict)
            assert 'payouts' in result
            assert len(result['payouts']) == 1
            assert result['total'] == 1
            assert result['page'] == 1
            assert result['limit'] == 10

    def test_list_user_accounts_with_all_optional_params(self):
        """Test list_user_accounts with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'accounts': [
                    {
                        'user_id': 123,
                        'external_id': 'ext_123',
                        'email': 'test@example.com'
                    }
                ],
                'total': 1,
                'offset': 0,
                'limit': 10
            }
            
            result = client.list_user_accounts(
                offset=0,
                limit=10,
                order='desc',
                order_by='created_at'
            )
            
            assert isinstance(result, dict)
            assert 'accounts' in result
            assert len(result['accounts']) == 1
            assert result['total'] == 1
            assert result['offset'] == 0
            assert result['limit'] == 10

    def test_list_transfers_with_all_optional_params(self):
        """Test list_transfers with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'transfers': [
                    {
                        'transfer_id': 'transfer_123',
                        'from_id': 123,
                        'to_id': 456,
                        'currency': 'btc',
                        'amount': '0.001',
                        'status': 'completed'
                    }
                ],
                'total': 1,
                'offset': 0,
                'limit': 10
            }
            
            result = client.list_transfers(
                user_id=123,
                status='completed',
                limit=10,
                offset=0,
                order='desc'
            )
            
            assert isinstance(result, dict)
            assert 'transfers' in result
            assert len(result['transfers']) == 1
            assert result['total'] == 1
            assert result['offset'] == 0
            assert result['limit'] == 10

    def test_list_conversions_with_all_optional_params(self):
        """Test list_conversions with all optional parameters."""
        client = NOWPayments('test_key')
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'conversions': [
                    {
                        'conversion_id': 'conv_123',
                        'from_currency': 'usd',
                        'to_currency': 'btc',
                        'from_amount': '100.00',
                        'to_amount': '0.001',
                        'status': 'completed'
                    }
                ],
                'total': 1,
                'offset': 0,
                'limit': 10
            }
            
            result = client.list_conversions(
                limit=10,
                offset=0
            )
            
            assert isinstance(result, dict)
            assert 'conversions' in result
            assert len(result['conversions']) == 1
            assert result['total'] == 1
            assert result['offset'] == 0
            assert result['limit'] == 10


if __name__ == "__main__":
    unittest.main() 