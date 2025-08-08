"""
Integration tests for the NOWPayments Python SDK.
These tests simulate real API interactions but use mocked responses.
"""

import unittest
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


class TestNOWPaymentsIntegration(unittest.TestCase):
    """Integration tests for the NOWPayments SDK."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = NOWPayments(
            api_key="test_api_key",
            sandbox=True
        )
    
    @patch('nowpayments.client.requests.Session.request')
    def test_complete_payment_workflow(self, mock_request):
        """Test a complete payment workflow from creation to status check."""
        # Step 1: Check API status
        mock_response_status = Mock()
        mock_response_status.status_code = 200
        mock_response_status.json.return_value = {"message": "OK"}
        
        # Step 2: Get currencies
        mock_response_currencies = Mock()
        mock_response_currencies.status_code = 200
        mock_response_currencies.json.return_value = {"currencies": ["btc", "eth", "ltc"]}
        
        # Step 3: Get estimate
        mock_response_estimate = Mock()
        mock_response_estimate.status_code = 200
        mock_response_estimate.json.return_value = {
            "amount_from": 100.0,
            "currency_from": "usd",
            "currency_to": "btc",
            "estimated_amount": 0.0045
        }
        
        # Step 4: Create payment
        mock_response_payment = Mock()
        mock_response_payment.status_code = 200
        mock_response_payment.json.return_value = {
            "payment_id": 123456789,
            "payment_status": "waiting",
            "pay_address": "test_address",
            "price_amount": 100.0,
            "price_currency": "usd",
            "pay_amount": 0.0045,
            "pay_currency": "btc",
            "order_id": "test_order_123",
            "created_at": "2023-01-01T12:00:00Z"
        }
        
        # Step 5: Check payment status
        mock_response_status_check = Mock()
        mock_response_status_check.status_code = 200
        mock_response_status_check.json.return_value = {
            "payment_id": 123456789,
            "payment_status": "confirmed",
            "pay_address": "test_address",
            "price_amount": 100.0,
            "price_currency": "usd",
            "pay_amount": 0.0045,
            "pay_currency": "btc",
            "order_id": "test_order_123",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:30:00Z",
            "purchase_id": "test_purchase_123",
            "outcome_amount": 0.0045,
            "outcome_currency": "btc"
        }
        
        mock_request.side_effect = [
            mock_response_status,
            mock_response_currencies,
            mock_response_estimate,
            mock_response_payment,
            mock_response_status_check
        ]
        
        # Execute the workflow
        # Step 1: Check API status
        status = self.client.get_status()
        self.assertEqual(status["message"], "OK")
        
        # Step 2: Get available currencies
        currencies = self.client.get_currencies()
        self.assertIn("btc", currencies)
        self.assertIn("eth", currencies)
        
        # Step 3: Get price estimate
        estimate = self.client.get_estimate(100.0, "usd", "btc")
        self.assertIsInstance(estimate, Estimate)
        self.assertEqual(estimate.amount_from, Decimal("100.0"))
        self.assertEqual(estimate.estimated_amount, Decimal("0.0045"))
        
        # Step 4: Create payment
        payment = self.client.create_payment(
            price_amount=100.0,
            price_currency="usd",
            pay_currency="btc",
            order_id="test_order_123"
        )
        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.payment_id, 123456789)
        self.assertEqual(payment.payment_status, "waiting")
        
        # Step 5: Check payment status
        payment_status = self.client.get_payment_status(123456789)
        self.assertIsInstance(payment_status, PaymentStatus)
        self.assertEqual(payment_status.payment_status, "confirmed")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_subscription_workflow(self, mock_request):
        """Test a complete subscription workflow."""
        # Step 1: Create subscription plan
        mock_response_plan = Mock()
        mock_response_plan.status_code = 200
        mock_response_plan.json.return_value = {
            "id": "test_plan_id",
            "title": "Test Plan",
            "interval_day": 30,
            "amount": 50.0,
            "currency": "usd"
        }
        
        # Step 2: Create subscription
        mock_response_subscription = Mock()
        mock_response_subscription.status_code = 200
        mock_response_subscription.json.return_value = {
            "subscription_id": "test_subscription_id",
            "plan_id": "test_plan_id",
            "email": "test@example.com",
            "status": "active",
            "order_id": "test_order_123"
        }
        
        # Step 3: Get subscription details
        mock_response_subscription_details = Mock()
        mock_response_subscription_details.status_code = 200
        mock_response_subscription_details.json.return_value = {
            "subscription_id": "test_subscription_id",
            "plan_id": "test_plan_id",
            "email": "test@example.com",
            "status": "active",
            "order_id": "test_order_123"
        }
        
        mock_request.side_effect = [
            mock_response_plan,
            mock_response_subscription,
            mock_response_subscription_details
        ]
        
        # Execute the workflow
        # Step 1: Create subscription plan
        plan = self.client.create_subscription_plan(
            title="Test Plan",
            interval_day=30,
            amount=50.0,
            currency="usd"
        )
        self.assertIsInstance(plan, SubscriptionPlan)
        self.assertEqual(plan.id, "test_plan_id")
        
        # Step 2: Create subscription
        subscription = self.client.create_subscription(
            plan_id="test_plan_id",
            email="test@example.com",
            order_id="test_order_123"
        )
        self.assertIsInstance(subscription, Subscription)
        self.assertEqual(subscription.subscription_id, "test_subscription_id")
        
        # Step 3: Get subscription details
        subscription_details = self.client.get_subscription("test_subscription_id")
        self.assertIsInstance(subscription_details, Subscription)
        self.assertEqual(subscription_details.status, "active")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_payout_workflow(self, mock_request):
        """Test a complete payout workflow."""
        # Step 1: Create payout
        mock_response_payout = Mock()
        mock_response_payout.status_code = 200
        mock_response_payout.json.return_value = {
            "batch_id": "test_batch_id",
            "withdrawals": [
                {
                    "id": "test_withdrawal_id",
                    "address": "test_address",
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "pending"
                }
            ],
            "status": "pending"
        }
        
        # Step 2: Verify payout
        mock_response_verify = Mock()
        mock_response_verify.status_code = 200
        mock_response_verify.json.return_value = {
            "batch_id": "test_batch_id",
            "withdrawals": [
                {
                    "id": "test_withdrawal_id",
                    "address": "test_address",
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "confirmed"
                }
            ],
            "status": "confirmed"
        }
        
        # Step 3: Get payout status
        mock_response_status = Mock()
        mock_response_status.status_code = 200
        mock_response_status.json.return_value = {
            "batch_id": "test_batch_id",
            "withdrawals": [
                {
                    "id": "test_withdrawal_id",
                    "address": "test_address",
                    "currency": "btc",
                    "amount": 0.001,
                    "status": "confirmed"
                }
            ],
            "status": "confirmed"
        }
        
        mock_request.side_effect = [
            mock_response_payout,
            mock_response_verify,
            mock_response_status
        ]
        
        # Execute the workflow
        # Step 1: Create payout
        withdrawals = [
            {
                "address": "test_address",
                "currency": "btc",
                "amount": 0.001
            }
        ]
        
        payout = self.client.create_payout(withdrawals=withdrawals)
        self.assertIsInstance(payout, PayoutBatch)
        self.assertEqual(payout.batch_id, "test_batch_id")
        
        # Step 2: Verify payout
        verified_payout = self.client.verify_payout(
            batch_id="test_batch_id",
            code="123456"
        )
        self.assertIsInstance(verified_payout, PayoutBatch)
        self.assertEqual(verified_payout.status, "confirmed")
        
        # Step 3: Get payout status
        payout_status = self.client.get_payout_status("test_batch_id")
        self.assertIsInstance(payout_status, PayoutBatch)
        self.assertEqual(payout_status.status, "confirmed")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_custody_workflow(self, mock_request):
        """Test a complete custody workflow."""
        # Step 1: Create user account
        mock_response_create_user = Mock()
        mock_response_create_user.status_code = 200
        mock_response_create_user.json.return_value = {
            "user_id": 123,
            "external_id": "test_external_id",
            "email": "test@example.com",
            "balance": {
                "btc": 0.0,
                "eth": 0.0
            }
        }
        
        # Step 2: Get user balance
        mock_response_balance = Mock()
        mock_response_balance.status_code = 200
        mock_response_balance.json.return_value = {
            "user_id": 123,
            "external_id": "test_external_id",
            "email": "test@example.com",
            "balance": {
                "btc": 0.001,
                "eth": 0.01
            }
        }
        
        # Step 3: Create user payment
        mock_response_payment = Mock()
        mock_response_payment.status_code = 200
        mock_response_payment.json.return_value = {
            "payment_id": 123456789,
            "payment_status": "waiting",
            "pay_address": "test_address",
            "price_amount": 50.0,
            "price_currency": "usd",
            "pay_amount": 0.002,
            "pay_currency": "btc",
            "user_id": 123
        }
        
        mock_request.side_effect = [
            mock_response_create_user,
            mock_response_balance,
            mock_response_payment
        ]
        
        # Execute the workflow
        # Step 1: Create user account
        user = self.client.create_user_account(
            external_id="test_external_id",
            email="test@example.com"
        )
        self.assertIsInstance(user, UserAccount)
        self.assertEqual(user.user_id, 123)
        
        # Step 2: Get user balance
        balance = self.client.get_user_balance(123)
        self.assertIsInstance(balance, UserAccount)
        self.assertEqual(balance.user_id, 123)
        
        # Step 3: Create user payment
        payment = self.client.create_user_payment(
            user_id=123,
            currency="btc",
            amount=0.002
        )
        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.payment_id, 123456789)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_conversion_workflow(self, mock_request):
        """Test a complete conversion workflow."""
        # Step 1: Create conversion
        mock_response_create = Mock()
        mock_response_create.status_code = 200
        mock_response_create.json.return_value = {
            "conversion_id": "test_conversion_id",
            "from_currency": "usd",
            "to_currency": "btc",
            "from_amount": 100.0,
            "to_amount": 0.0045,
            "status": "pending"
        }
        
        # Step 2: Get conversion status
        mock_response_status = Mock()
        mock_response_status.status_code = 200
        mock_response_status.json.return_value = {
            "conversion_id": "test_conversion_id",
            "from_currency": "usd",
            "to_currency": "btc",
            "from_amount": 100.0,
            "to_amount": 0.0045,
            "status": "confirmed"
        }
        
        mock_request.side_effect = [
            mock_response_create,
            mock_response_status
        ]
        
        # Execute the workflow
        # Step 1: Create conversion
        conversion = self.client.create_conversion(
            from_currency="usd",
            to_currency="btc",
            amount=100.0
        )
        self.assertIsInstance(conversion, Conversion)
        self.assertEqual(conversion.conversion_id, "test_conversion_id")
        
        # Step 2: Get conversion status
        conversion_status = self.client.get_conversion_status("test_conversion_id")
        self.assertIsInstance(conversion_status, Conversion)
        self.assertEqual(conversion_status.status, "confirmed")
    
    @patch('nowpayments.client.requests.Session.request')
    def test_error_handling_integration(self, mock_request):
        """Test error handling in real-world scenarios."""
        # Test authentication error
        mock_response_auth_error = Mock()
        mock_response_auth_error.status_code = 401
        mock_response_auth_error.json.return_value = {"message": "Invalid API key"}
        
        mock_request.return_value = mock_response_auth_error
        
        with self.assertRaises(AuthenticationError):
            self.client.get_status()
        
        # Test rate limit error
        mock_response_rate_limit = Mock()
        mock_response_rate_limit.status_code = 429
        mock_response_rate_limit.json.return_value = {"message": "Rate limit exceeded"}
        
        mock_request.return_value = mock_response_rate_limit
        
        with self.assertRaises(RateLimitError):
            self.client.get_status()
        
        # Test payment error
        mock_response_payment_error = Mock()
        mock_response_payment_error.status_code = 400
        mock_response_payment_error.json.return_value = {"message": "Payment error"}
        
        mock_request.return_value = mock_response_payment_error
        
        with self.assertRaises(PaymentError):
            self.client.create_payment(
                price_amount=100.0,
                price_currency="usd",
                pay_currency="btc"
            )
    
    def test_ipn_verification_integration(self):
        """Test IPN verification in real-world scenarios."""
        verifier = IPNVerifier(ipn_secret="test_secret")
        
        # Test valid IPN data
        import hmac
        import hashlib
        import json
        
        ipn_data = {
            "payment_id": 123456789,
            "payment_status": "confirmed",
            "pay_address": "test_address",
            "price_amount": 100.0,
            "price_currency": "usd",
            "pay_amount": 0.0045,
            "pay_currency": "btc"
        }
        
        # Generate valid signature
        sorted_data = dict(sorted(ipn_data.items()))
        json_string = json.dumps(sorted_data, separators=(',', ':'))
        expected_signature = hmac.new(
            b"test_secret",
            json_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Test verification
        headers = {"X-NOWPAYMENTS-Sig": expected_signature}
        result = verifier.verify_request(ipn_data, headers)
        self.assertTrue(result)
        
        # Test invalid signature
        headers_invalid = {"X-NOWPAYMENTS-Sig": "invalid_signature"}
        result_invalid = verifier.verify_request(ipn_data, headers_invalid)
        self.assertFalse(result_invalid)
        
        # Test missing signature
        headers_missing = {}
        result_missing = verifier.verify_request(ipn_data, headers_missing)
        self.assertFalse(result_missing)


class TestNOWPaymentsEndToEnd(unittest.TestCase):
    """End-to-end tests that simulate complete user workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = NOWPayments(
            api_key="test_api_key",
            sandbox=True
        )
    
    @patch('nowpayments.client.requests.Session.request')
    def test_ecommerce_integration(self, mock_request):
        """Test a complete e-commerce integration scenario."""
        # Mock responses for a complete e-commerce flow
        responses = [
            # API status check
            Mock(status_code=200, json=lambda: {"message": "OK"}),
            # Get currencies
            Mock(status_code=200, json=lambda: {"currencies": ["btc", "eth", "ltc"]}),
            # Get estimate
            Mock(status_code=200, json=lambda: {
                "amount_from": 99.99,
                "currency_from": "usd",
                "currency_to": "btc",
                "estimated_amount": 0.0042
            }),
            # Create payment
            Mock(status_code=200, json=lambda: {
                "payment_id": 987654321,
                "payment_status": "waiting",
                "pay_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "price_amount": 99.99,
                "price_currency": "usd",
                "pay_amount": 0.0042,
                "pay_currency": "btc",
                "order_id": "order_12345",
                "created_at": "2023-01-01T12:00:00Z"
            }),
            # Check payment status (pending)
            Mock(status_code=200, json=lambda: {
                "payment_id": 987654321,
                "payment_status": "waiting",
                "pay_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "price_amount": 99.99,
                "price_currency": "usd",
                "pay_amount": 0.0042,
                "pay_currency": "btc",
                "order_id": "order_12345",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:05:00Z"
            }),
            # Check payment status (confirmed)
            Mock(status_code=200, json=lambda: {
                "payment_id": 987654321,
                "payment_status": "confirmed",
                "pay_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "price_amount": 99.99,
                "price_currency": "usd",
                "pay_amount": 0.0042,
                "pay_currency": "btc",
                "order_id": "order_12345",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:30:00Z",
                "purchase_id": "purchase_12345",
                "outcome_amount": 0.0042,
                "outcome_currency": "btc"
            })
        ]
        
        mock_request.side_effect = responses
        
        # Simulate e-commerce workflow
        # 1. Check API status
        status = self.client.get_status()
        self.assertEqual(status["message"], "OK")
        
        # 2. Get available payment methods
        currencies = self.client.get_currencies()
        self.assertIn("btc", currencies)
        
        # 3. Get price estimate
        estimate = self.client.get_estimate(99.99, "usd", "btc")
        self.assertEqual(estimate.estimated_amount, Decimal("0.0042"))
        
        # 4. Create payment
        payment = self.client.create_payment(
            price_amount=99.99,
            price_currency="usd",
            pay_currency="btc",
            order_id="order_12345"
        )
        self.assertEqual(payment.payment_id, 987654321)
        self.assertEqual(payment.payment_status, "waiting")
        
        # 5. Monitor payment status
        status_pending = self.client.get_payment_status(987654321)
        self.assertEqual(status_pending.payment_status, "waiting")
        
        # 6. Payment confirmed
        status_confirmed = self.client.get_payment_status(987654321)
        self.assertEqual(status_confirmed.payment_status, "confirmed")
        
        # Verify all expected calls were made
        self.assertEqual(mock_request.call_count, 6)
    
    @patch('nowpayments.client.requests.Session.request')
    def test_subscription_service_integration(self, mock_request):
        """Test a complete subscription service integration."""
        # Mock responses for subscription service
        responses = [
            # Create subscription plan
            Mock(status_code=200, json=lambda: {
                "id": "premium_monthly",
                "title": "Premium Monthly",
                "interval_day": 30,
                "amount": 29.99,
                "currency": "usd"
            }),
            # Create subscription
            Mock(status_code=200, json=lambda: {
                "subscription_id": "sub_12345",
                "plan_id": "premium_monthly",
                "email": "customer@example.com",
                "status": "active",
                "order_id": "order_sub_12345"
            }),
            # Get subscription details
            Mock(status_code=200, json=lambda: {
                "subscription_id": "sub_12345",
                "plan_id": "premium_monthly",
                "email": "customer@example.com",
                "status": "active",
                "order_id": "order_sub_12345",
                "next_payment_date": "2023-02-01T12:00:00Z"
            }),
            # List subscriptions
            Mock(status_code=200, json=lambda: {
                "subscriptions": [
                    {
                        "subscription_id": "sub_12345",
                        "plan_id": "premium_monthly",
                        "email": "customer@example.com",
                        "status": "active"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 10
            })
        ]
        
        mock_request.side_effect = responses
        
        # Simulate subscription service workflow
        # 1. Create subscription plan
        plan = self.client.create_subscription_plan(
            title="Premium Monthly",
            interval_day=30,
            amount=29.99,
            currency="usd"
        )
        self.assertEqual(plan.id, "premium_monthly")
        
        # 2. Create subscription
        subscription = self.client.create_subscription(
            plan_id="premium_monthly",
            email="customer@example.com",
            order_id="order_sub_12345"
        )
        self.assertEqual(subscription.subscription_id, "sub_12345")
        
        # 3. Get subscription details
        details = self.client.get_subscription("sub_12345")
        self.assertEqual(details.status, "active")
        
        # 4. List all subscriptions
        subscriptions = self.client.list_subscriptions()
        self.assertEqual(subscriptions["total"], 1)
        self.assertEqual(len(subscriptions["subscriptions"]), 1)
        
        # Verify all expected calls were made
        self.assertEqual(mock_request.call_count, 4)


if __name__ == "__main__":
    unittest.main() 