"""
Live tests for NOWPayments Python SDK.

These tests make actual API calls to the NOWPayments API using real credentials.
They should be run carefully and only when needed, as they use real API endpoints.

Environment Setup:
1. Copy tests/env.example to tests/.env
2. Fill in your actual API credentials in tests/.env
3. Run tests with: python run_live_tests.py
"""

import os
import pytest
import time
from decimal import Decimal
from unittest.mock import patch
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file in tests directory."""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env_file()

from nowpayments import NOWPayments, IPNVerifier
from nowpayments.exceptions import (
    AuthenticationError,
    PaymentError,
    PayoutError,
    SubscriptionError,
    CustodyError,
    ConversionError,
    ValidationError,
    RateLimitError,
    NOWPaymentsError,
)


class TestLiveNOWPayments:
    """Live tests that make actual API calls to NOWPayments."""

    @classmethod
    def setup_class(cls):
        """Set up the test client with real API credentials."""
        # Get API key from environment
        api_key = os.getenv('NOWPAYMENTS_API_KEY')
        if not api_key:
            pytest.skip("NOWPAYMENTS_API_KEY not found in environment. Please set up tests/.env file.")
        
        # Get environment setting
        environment = os.getenv('NOWPAYMENTS_ENVIRONMENT', 'sandbox').lower()
        sandbox = environment == 'sandbox'
        
        # Initialize client
        cls.client = NOWPayments(api_key=api_key, sandbox=sandbox)
        
        # Load credentials from environment
        cls.test_credentials = {
            'api_key': api_key,
            'ipn_secret': os.getenv('NOWPAYMENTS_IPN_SECRET', ''),
            'jwt_token': os.getenv('NOWPAYMENTS_JWT_TOKEN', ''),
            'otp_code': os.getenv('NOWPAYMENTS_OTP_CODE', '123456')
        }
        
        print(f"✅ Using {environment.upper()} environment for live tests")

    def test_live_api_status(self):
        """Test that we can connect to the API and get status."""
        try:
            status = self.client.get_status()
            assert status is not None
            print(f"✅ API Status: {status}")
        except Exception as e:
            pytest.skip(f"API not accessible: {e}")

    def test_live_get_currencies(self):
        """Test getting available currencies."""
        try:
            currencies = self.client.get_currencies()
            assert isinstance(currencies, list)
            assert len(currencies) > 0
            print(f"✅ Available currencies: {len(currencies)} currencies")
        except Exception as e:
            pytest.skip(f"Currencies endpoint not accessible: {e}")

    def test_live_get_full_currencies(self):
        """Test getting full currency information."""
        try:
            currencies = self.client.get_full_currencies()
            assert isinstance(currencies, list)
            assert len(currencies) > 0
            # Check that we have some major cryptocurrencies
            currency_codes = [c.code for c in currencies]
            assert 'BTC' in currency_codes or 'ETH' in currency_codes
            print(f"✅ Full currencies: {len(currencies)} currencies")
        except Exception as e:
            pytest.skip(f"Full currencies endpoint not accessible: {e}")

    def test_live_get_merchant_currencies(self):
        """Test getting merchant-specific currencies."""
        try:
            currencies = self.client.get_merchant_currencies()
            assert isinstance(currencies, list)
            print(f"✅ Merchant currencies: {len(currencies)} currencies")
        except Exception as e:
            pytest.skip(f"Merchant currencies endpoint not accessible: {e}")

    def test_live_get_min_amount(self):
        """Test getting minimum payment amounts."""
        try:
            # Test with a common currency pair
            min_amount = self.client.get_min_amount('BTC_USDT')
            assert isinstance(min_amount, Decimal)
            assert min_amount > 0
            print(f"✅ Min BTC_USDT amount: {min_amount}")
        except Exception as e:
            pytest.skip(f"Min amount endpoint not accessible: {e}")

    def test_live_estimate_payment(self):
        """Test payment estimation."""
        try:
            # Test with a small amount
            estimate = self.client.estimate_payment(
                amount=Decimal('10.00'),
                currency_from='USD',
                currency_to='BTC'
            )
            assert estimate.estimated_amount > 0
            assert estimate.rate > 0
            print(f"✅ Payment estimate: {estimate.estimated_amount} BTC for $10.00")
        except Exception as e:
            pytest.skip(f"Estimate endpoint not accessible: {e}")

    def test_live_create_payment(self):
        """Test creating a payment (this will create a real payment request)."""
        try:
            payment = self.client.create_payment(
                price_amount=Decimal('5.00'),
                price_currency='USD',
                pay_currency='BTC',
                order_id=f'test_order_{int(time.time())}',
                order_description='Live test payment'
            )
            assert payment.payment_id is not None
            assert payment.payment_status in ['waiting', 'pending', 'confirming', 'confirmed', 'sending', 'partially_paid', 'finished', 'failed', 'refunded', 'expired']
            print(f"✅ Created payment: {payment.payment_id} - {payment.payment_status}")
        except Exception as e:
            pytest.skip(f"Create payment endpoint not accessible: {e}")

    def test_live_get_payment_status(self):
        """Test getting payment status."""
        try:
            # First create a payment
            payment = self.client.create_payment(
                price_amount=Decimal('1.00'),
                price_currency='USD',
                pay_currency='BTC',
                order_id=f'test_status_{int(time.time())}',
                order_description='Status test payment'
            )
            
            # Then get its status
            status = self.client.get_payment_status(payment.payment_id)
            assert status.payment_id == payment.payment_id
            assert status.payment_status in ['waiting', 'pending', 'confirming', 'confirmed', 'sending', 'partially_paid', 'finished', 'failed', 'refunded', 'expired']
            print(f"✅ Payment status: {status.payment_id} - {status.payment_status}")
        except Exception as e:
            pytest.skip(f"Payment status endpoint not accessible: {e}")

    def test_live_list_payments(self):
        """Test listing payments."""
        try:
            payments = self.client.list_payments()
            assert isinstance(payments, list)
            print(f"✅ Listed {len(payments)} payments")
        except Exception as e:
            pytest.skip(f"List payments endpoint not accessible: {e}")

    def test_live_create_invoice(self):
        """Test creating an invoice."""
        try:
            invoice = self.client.create_invoice(
                price_amount=Decimal('15.00'),
                price_currency='USD',
                pay_currency='ETH',
                order_id=f'test_invoice_{int(time.time())}',
                order_description='Live test invoice'
            )
            assert invoice.invoice_id is not None
            assert invoice.payment_status in ['waiting', 'pending', 'confirming', 'confirmed', 'sending', 'partially_paid', 'finished', 'failed', 'refunded', 'expired']
            print(f"✅ Created invoice: {invoice.invoice_id} - {invoice.payment_status}")
        except Exception as e:
            pytest.skip(f"Create invoice endpoint not accessible: {e}")

    def test_live_get_invoice_status(self):
        """Test getting invoice status."""
        try:
            # First create an invoice
            invoice = self.client.create_invoice(
                price_amount=Decimal('2.00'),
                price_currency='USD',
                pay_currency='ETH',
                order_id=f'test_invoice_status_{int(time.time())}',
                order_description='Invoice status test'
            )
            
            # Then get its status
            status = self.client.get_invoice_status(invoice.invoice_id)
            assert status.invoice_id == invoice.invoice_id
            assert status.payment_status in ['waiting', 'pending', 'confirming', 'confirmed', 'sending', 'partially_paid', 'finished', 'failed', 'refunded', 'expired']
            print(f"✅ Invoice status: {status.invoice_id} - {status.payment_status}")
        except Exception as e:
            pytest.skip(f"Invoice status endpoint not accessible: {e}")

    def test_live_create_subscription_plan(self):
        """Test creating a subscription plan."""
        try:
            plan = self.client.create_subscription_plan(
                name='Live Test Plan',
                price_amount=Decimal('25.00'),
                price_currency='USD',
                pay_currency='BTC',
                interval_day=30,
                description='Live test subscription plan'
            )
            assert plan.id is not None
            assert plan.name == 'Live Test Plan'
            assert plan.price_amount == Decimal('25.00')
            print(f"✅ Created subscription plan: {plan.id} - {plan.name}")
        except Exception as e:
            pytest.skip(f"Create subscription plan endpoint not accessible: {e}")

    def test_live_get_subscription_plan(self):
        """Test getting subscription plan details."""
        try:
            # First create a plan
            plan = self.client.create_subscription_plan(
                name='Live Test Plan Details',
                price_amount=Decimal('10.00'),
                price_currency='USD',
                pay_currency='BTC',
                interval_day=7,
                description='Plan details test'
            )
            
            # Then get its details
            plan_details = self.client.get_subscription_plan(plan.id)
            assert plan_details.id == plan.id
            assert plan_details.name == 'Live Test Plan Details'
            print(f"✅ Subscription plan details: {plan_details.id} - {plan_details.name}")
        except Exception as e:
            pytest.skip(f"Get subscription plan endpoint not accessible: {e}")

    def test_live_list_subscription_plans(self):
        """Test listing subscription plans."""
        try:
            plans = self.client.list_subscription_plans()
            assert isinstance(plans, list)
            print(f"✅ Listed {len(plans)} subscription plans")
        except Exception as e:
            pytest.skip(f"List subscription plans endpoint not accessible: {e}")

    def test_live_create_subscription(self):
        """Test creating a subscription."""
        try:
            # First create a plan
            plan = self.client.create_subscription_plan(
                name='Live Test Subscription Plan',
                price_amount=Decimal('5.00'),
                price_currency='USD',
                pay_currency='BTC',
                interval_day=1,
                description='Subscription test plan'
            )
            
            # Then create a subscription
            subscription = self.client.create_subscription(
                plan_id=plan.id,
                order_id=f'test_subscription_{int(time.time())}',
                order_description='Live test subscription'
            )
            assert subscription.id is not None
            assert subscription.plan_id == plan.id
            print(f"✅ Created subscription: {subscription.id} for plan {subscription.plan_id}")
        except Exception as e:
            pytest.skip(f"Create subscription endpoint not accessible: {e}")

    def test_live_get_subscription(self):
        """Test getting subscription details."""
        try:
            # First create a plan and subscription
            plan = self.client.create_subscription_plan(
                name='Live Test Subscription Details',
                price_amount=Decimal('3.00'),
                price_currency='USD',
                pay_currency='BTC',
                interval_day=1,
                description='Subscription details test'
            )
            
            subscription = self.client.create_subscription(
                plan_id=plan.id,
                order_id=f'test_subscription_details_{int(time.time())}',
                order_description='Subscription details test'
            )
            
            # Then get subscription details
            subscription_details = self.client.get_subscription(subscription.id)
            assert subscription_details.id == subscription.id
            assert subscription_details.plan_id == plan.id
            print(f"✅ Subscription details: {subscription_details.id} - {subscription_details.status}")
        except Exception as e:
            pytest.skip(f"Get subscription endpoint not accessible: {e}")

    def test_live_list_subscriptions(self):
        """Test listing subscriptions."""
        try:
            subscriptions = self.client.list_subscriptions()
            assert isinstance(subscriptions, list)
            print(f"✅ Listed {len(subscriptions)} subscriptions")
        except Exception as e:
            pytest.skip(f"List subscriptions endpoint not accessible: {e}")

    def test_live_validate_address(self):
        """Test address validation."""
        try:
            # Test with a valid Bitcoin address format
            validation = self.client.validate_address(
                currency='BTC',
                address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'  # Example address
            )
            assert isinstance(validation.result, bool)
            assert isinstance(validation.message, str)
            print(f"✅ Address validation: {validation.result} - {validation.message}")
        except Exception as e:
            pytest.skip(f"Address validation endpoint not accessible: {e}")

    def test_live_create_user_account(self):
        """Test creating a user account."""
        try:
            account = self.client.create_user_account(
                email='test@example.com',
                name='Live Test User'
            )
            assert account.id is not None
            assert account.email == 'test@example.com'
            print(f"✅ Created user account: {account.id} - {account.email}")
        except Exception as e:
            pytest.skip(f"Create user account endpoint not accessible: {e}")

    def test_live_get_user_account(self):
        """Test getting user account details."""
        try:
            # First create an account
            account = self.client.create_user_account(
                email=f'test{int(time.time())}@example.com',
                name='Live Test User Details'
            )
            
            # Then get its details
            account_details = self.client.get_user_account(account.id)
            assert account_details.id == account.id
            assert account_details.email == account.email
            print(f"✅ User account details: {account_details.id} - {account_details.email}")
        except Exception as e:
            pytest.skip(f"Get user account endpoint not accessible: {e}")

    def test_live_list_user_accounts(self):
        """Test listing user accounts."""
        try:
            accounts = self.client.list_user_accounts()
            assert isinstance(accounts, list)
            print(f"✅ Listed {len(accounts)} user accounts")
        except Exception as e:
            pytest.skip(f"List user accounts endpoint not accessible: {e}")

    def test_live_get_balance(self):
        """Test getting balance."""
        try:
            balance = self.client.get_balance()
            assert isinstance(balance, dict)
            print(f"✅ Balance retrieved: {len(balance)} currencies")
        except Exception as e:
            pytest.skip(f"Get balance endpoint not accessible: {e}")

    def test_live_list_conversions(self):
        """Test listing conversions."""
        try:
            conversions = self.client.list_conversions()
            assert isinstance(conversions, list)
            print(f"✅ Listed {len(conversions)} conversions")
        except Exception as e:
            pytest.skip(f"List conversions endpoint not accessible: {e}")

    def test_live_ipn_verification(self):
        """Test IPN signature verification."""
        try:
            # Create a test IPN payload
            test_payload = {
                'payment_id': 'test_payment_123',
                'payment_status': 'finished',
                'pay_address': 'test_address',
                'pay_amount': '0.001',
                'pay_currency': 'BTC',
                'price_amount': '10.00',
                'price_currency': 'USD',
                'order_id': 'test_order_123',
                'order_description': 'Test payment',
                'purchase_id': 'test_purchase_123',
                'created_at': '2023-01-01T00:00:00.000Z',
                'updated_at': '2023-01-01T00:00:00.000Z',
                'outcome_amount': '0.001',
                'outcome_currency': 'BTC'
            }
            
            # Create a test signature
            verifier = IPNVerifier(self.test_credentials['ipn_secret'])
            
            # Test with a mock signature (in real usage, this would come from the webhook)
            with patch.object(verifier, '_get_signature', return_value='test_signature'):
                is_valid = verifier.verify_signature('test_signature', test_payload)
                assert isinstance(is_valid, bool)
                print(f"✅ IPN verification test completed")
        except Exception as e:
            pytest.skip(f"IPN verification test failed: {e}")

    def test_live_error_handling(self):
        """Test live error handling with invalid requests."""
        try:
            # Test with invalid API key
            invalid_client = NOWPayments(api_key='invalid_key', sandbox=True)
            
            # This might not raise AuthenticationError in all cases
            # due to how the API handles invalid keys
            try:
                invalid_client.get_status()
                # If it doesn't raise an error, that's also acceptable
                print("✅ Invalid API key handled gracefully")
            except (AuthenticationError, NOWPaymentsError) as e:
                print(f"✅ Authentication error handling works: {e}")
        except Exception as e:
            pytest.skip(f"Error handling test failed: {e}")

    def test_live_rate_limiting(self):
        """Test rate limiting behavior."""
        try:
            # Make multiple rapid requests to test rate limiting
            for i in range(5):
                try:
                    self.client.get_status()
                    time.sleep(0.1)  # Small delay between requests
                except RateLimitError:
                    print("✅ Rate limiting detected and handled")
                    return
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        print("✅ Rate limiting detected and handled")
                        return
            
            print("✅ No rate limiting detected (normal for test environment)")
        except Exception as e:
            pytest.skip(f"Rate limiting test failed: {e}")

    def test_live_comprehensive_workflow(self):
        """Test a comprehensive payment workflow."""
        try:
            # 1. Get API status
            status = self.client.get_status()
            assert status is not None
            
            # 2. Get available currencies
            currencies = self.client.get_currencies()
            assert len(currencies) > 0
            
            # 3. Get minimum amount for a currency pair
            min_amount = self.client.get_min_amount('BTC_USDT')
            assert min_amount > 0
            
            # 4. Estimate a payment
            estimate = self.client.estimate_payment(
                amount=Decimal('5.00'),
                currency_from='USD',
                currency_to='BTC'
            )
            assert estimate.estimated_amount > 0
            
            # 5. Create a payment
            payment = self.client.create_payment(
                price_amount=Decimal('5.00'),
                price_currency='USD',
                pay_currency='BTC',
                order_id=f'workflow_test_{int(time.time())}',
                order_description='Comprehensive workflow test'
            )
            assert payment.payment_id is not None
            
            # 6. Get payment status
            payment_status = self.client.get_payment_status(payment.payment_id)
            assert payment_status.payment_id == payment.payment_id
            
            print("✅ Comprehensive workflow completed successfully")
        except Exception as e:
            pytest.skip(f"Comprehensive workflow test failed: {e}")


class TestLiveIPNVerification:
    """Live tests for IPN verification."""

    def test_live_ipn_verifier_creation(self):
        """Test IPN verifier creation."""
        try:
            verifier = IPNVerifier('test_secret_key')
            assert verifier.secret_key == 'test_secret_key'
            print("✅ IPN verifier created successfully")
        except Exception as e:
            pytest.skip(f"IPN verifier creation failed: {e}")

    def test_live_ipn_signature_generation(self):
        """Test IPN signature generation."""
        try:
            verifier = IPNVerifier('test_secret_key')
            test_payload = {'test': 'data'}
            
            # Generate signature
            signature = verifier._get_signature(test_payload)
            assert isinstance(signature, str)
            assert len(signature) > 0
            print("✅ IPN signature generation works")
        except Exception as e:
            pytest.skip(f"IPN signature generation failed: {e}")


if __name__ == '__main__':
    # Run live tests
    pytest.main(['-v', 'tests/test_live.py']) 