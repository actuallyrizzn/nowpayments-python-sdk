"""
Basic usage example for the NOWPayments Python SDK.
"""

from nowpayments import NOWPayments

# Initialize the client
client = NOWPayments(
    api_key="YOUR_API_KEY_HERE",
    sandbox=True  # Use sandbox for testing
)

def main():
    """Demonstrate basic SDK usage."""
    
    print("=== NOWPayments Python SDK - Basic Usage Example ===\n")
    
    # 1. Check API status
    print("1. Checking API status...")
    try:
        status = client.get_status()
        print(f"   API Status: {status}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Get available currencies
    print("\n2. Getting available currencies...")
    try:
        currencies = client.get_currencies()
        print(f"   Available currencies: {currencies[:5]}...")  # Show first 5
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Get merchant's active currencies
    print("\n3. Getting merchant's active currencies...")
    try:
        merchant_currencies = client.get_merchant_currencies()
        print(f"   Merchant currencies: {merchant_currencies}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Get price estimate
    print("\n4. Getting price estimate...")
    try:
        estimate = client.get_estimate(
            amount=100.00,
            currency_from="usd",
            currency_to="btc"
        )
        print(f"   {estimate.amount_from} {estimate.currency_from} = {estimate.estimated_amount} {estimate.currency_to}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 5. Get minimum payment amount
    print("\n5. Getting minimum payment amount...")
    try:
        min_amount = client.get_min_amount("btc", "usd")
        print(f"   Minimum amount: {min_amount}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 6. Create a payment (commented out to avoid actual payment creation)
    print("\n6. Creating a payment (commented out)...")
    """
    try:
        payment = client.create_payment(
            price_amount=10.00,
            price_currency="usd",
            pay_currency="btc",
            order_id="test_order_123",
            order_description="Test payment from SDK"
        )
        print(f"   Payment created: {payment.payment_id}")
        print(f"   Pay address: {payment.pay_address}")
        print(f"   Amount to pay: {payment.pay_amount} {payment.pay_currency}")
    except Exception as e:
        print(f"   Error: {e}")
    """
    print("   (Payment creation commented out to avoid actual payments)")
    
    print("\n=== Example completed ===")

if __name__ == "__main__":
    main() 