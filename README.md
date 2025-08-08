# NOWPayments Python SDK

Official Python SDK for the NOWPayments API - the easiest way to integrate cryptocurrency payments into your Python applications.

## Features

- **Complete API Coverage**: All NOWPayments endpoints including payments, subscriptions, payouts, and custody
- **Type Safety**: Full type hints for better development experience
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Security**: Built-in support for API keys, IP whitelisting, and 2FA
- **Async Support**: Both synchronous and asynchronous API methods
- **Testing**: Extensive test coverage with pytest

## Installation

```bash
pip install nowpayments-python-sdk
```

## Quick Start

```python
from nowpayments import NOWPayments

# Initialize the client
client = NOWPayments(api_key="YOUR_API_KEY")

# Create a payment
payment = client.create_payment(
    price_amount=100.00,
    price_currency="usd",
    pay_currency="btc",
    order_id="order_123",
    order_description="Test payment"
)

print(f"Payment ID: {payment.payment_id}")
print(f"Pay Address: {payment.pay_address}")
print(f"Amount to pay: {payment.pay_amount} {payment.pay_currency}")

# Check payment status
status = client.get_payment_status(payment.payment_id)
print(f"Status: {status.payment_status}")
```

## API Key Setup

1. Sign up at [NOWPayments](https://nowpayments.io)
2. Generate your API key in the dashboard
3. Add your server's IP to the whitelist for sensitive operations

## Basic Usage

### Authentication

```python
from nowpayments import NOWPayments

# Initialize with your API key
client = NOWPayments(api_key="YOUR_API_KEY")

# For sandbox testing
client = NOWPayments(
    api_key="YOUR_SANDBOX_API_KEY",
    sandbox=True
)
```

### Creating Payments

```python
# Create a simple payment
payment = client.create_payment(
    price_amount=50.00,
    price_currency="usd",
    pay_currency="btc"
)

# Create payment with additional options
payment = client.create_payment(
    price_amount=100.00,
    price_currency="usd",
    pay_currency="eth",
    order_id="order_123",
    order_description="Premium subscription",
    ipn_callback_url="https://your-site.com/ipn",
    payout_address="0xYourWalletAddress",
    payout_currency="usdttrc20"
)
```

### Checking Payment Status

```python
# Get payment status
status = client.get_payment_status(payment_id=123456789)

if status.payment_status == "finished":
    print("Payment completed!")
elif status.payment_status == "waiting":
    print("Waiting for payment...")
```

### Handling IPN Callbacks

```python
from nowpayments import NOWPayments, IPNVerifier

# Verify IPN signature
verifier = IPNVerifier(ipn_secret="YOUR_IPN_SECRET")

@app.route("/ipn", methods=["POST"])
def handle_ipn():
    data = request.get_json()
    signature = request.headers.get("X-NOWPAYMENTS-Sig")
    
    if verifier.verify_signature(data, signature):
        # Process the payment update
        payment_id = data["payment_id"]
        status = data["payment_status"]
        # Handle the status change
        return "OK", 200
    else:
        return "Invalid signature", 400
```

### Recurring Payments (Subscriptions)

```python
# Create a subscription plan
plan = client.create_subscription_plan(
    title="Monthly Premium",
    interval_day=30,
    amount=29.99,
    currency="usd"
)

# Subscribe a customer
subscription = client.create_subscription(
    plan_id=plan.id,
    email="customer@example.com",
    order_id="sub_123"
)
```

### Mass Payouts

```python
# Create a payout batch (requires 2FA)
payout = client.create_payout(
    withdrawals=[
        {
            "address": "0xRecipientAddress",
            "currency": "eth",
            "amount": 0.1
        },
        {
            "address": "TRecipientAddress",
            "currency": "trx",
            "amount": 100
        }
    ]
)

# Verify with 2FA
client.verify_payout(payout.batch_id, "123456")
```

### Custody (Sub-Accounts)

```python
# Create a user account
user = client.create_user_account(
    external_id="user_123",
    email="user@example.com"
)

# Generate deposit address for user
deposit = client.create_user_payment(
    user_id=user.user_id,
    currency="btc",
    amount=0.01
)

# Transfer between users
transfer = client.transfer_funds(
    from_id=user1.user_id,
    to_id=user2.user_id,
    currency="usd",
    amount=50.00
)
```

## Advanced Features

### Currency Conversion

```python
# Convert funds within your account
conversion = client.create_conversion(
    from_currency="btc",
    to_currency="eth",
    amount=0.05
)
```

### Address Validation

```python
# Validate payout addresses
is_valid = client.validate_address(
    address="0xValidAddress",
    currency="eth"
)
```

### Price Estimation

```python
# Get price estimate
estimate = client.get_estimate(
    amount=100.00,
    currency_from="usd",
    currency_to="btc"
)
```

## Error Handling

```python
from nowpayments import NOWPaymentsError, PaymentError

try:
    payment = client.create_payment(...)
except PaymentError as e:
    print(f"Payment error: {e}")
except NOWPaymentsError as e:
    print(f"API error: {e}")
```

## Configuration

### Environment Variables

```python
import os
from nowpayments import NOWPayments

client = NOWPayments(
    api_key=os.getenv("NOWPAYMENTS_API_KEY"),
    sandbox=os.getenv("NOWPAYMENTS_SANDBOX", "false").lower() == "true"
)
```

### Custom Configuration

```python
from nowpayments import NOWPayments

client = NOWPayments(
    api_key="YOUR_API_KEY",
    sandbox=True,
    timeout=30,
    retries=3
)
```

## Development

### Installing for Development

```bash
git clone https://github.com/nowpayments/nowpayments-python-sdk.git
cd nowpayments-python-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nowpayments --cov-report=html

# Run live tests (requires API credentials)
# First, copy tests/env.example to tests/.env and fill in your credentials
cp tests/env.example tests/.env
# Edit tests/.env with your actual API credentials
python run_live_tests.py

# Run specific live test
python run_live_tests.py --test test_live_api_status
```

### Code Formatting

```bash
black nowpayments/
flake8 nowpayments/
mypy nowpayments/
```

## Documentation

For detailed API documentation, visit [NOWPayments API Docs](https://nowpayments.io/docs).

## Support

- **Documentation**: [https://nowpayments.io/docs](https://nowpayments.io/docs)
- **API Reference**: [https://api.nowpayments.io](https://api.nowpayments.io)
- **Support**: [support@nowpayments.io](mailto:support@nowpayments.io)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 