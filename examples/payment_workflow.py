"""
Complete payment workflow example for the NOWPayments Python SDK.
"""

from nowpayments import NOWPayments, IPNVerifier
import time

# Initialize the client
client = NOWPayments(
    api_key="YOUR_API_KEY_HERE",
    sandbox=True  # Use sandbox for testing
)

def payment_workflow_example():
    """Demonstrate a complete payment workflow."""
    
    print("=== NOWPayments Payment Workflow Example ===\n")
    
    # Step 1: Check API status
    print("Step 1: Checking API status...")
    try:
        status = client.get_status()
        print(f"   ✓ API is operational: {status}")
    except Exception as e:
        print(f"   ✗ API error: {e}")
        return
    
    # Step 2: Get available currencies
    print("\nStep 2: Getting available currencies...")
    try:
        currencies = client.get_currencies()
        print(f"   ✓ Available currencies: {len(currencies)} currencies")
        print(f"   Sample currencies: {currencies[:5]}")
    except Exception as e:
        print(f"   ✗ Error getting currencies: {e}")
        return
    
    # Step 3: Get price estimate
    print("\nStep 3: Getting price estimate...")
    try:
        estimate = client.get_estimate(
            amount=50.00,
            currency_from="usd",
            currency_to="btc"
        )
        print(f"   ✓ Price estimate: {estimate.amount_from} {estimate.currency_from} = {estimate.estimated_amount} {estimate.currency_to}")
    except Exception as e:
        print(f"   ✗ Error getting estimate: {e}")
        return
    
    # Step 4: Get minimum payment amount
    print("\nStep 4: Getting minimum payment amount...")
    try:
        min_amount = client.get_min_amount("btc", "usd")
        print(f"   ✓ Minimum payment amount: {min_amount}")
    except Exception as e:
        print(f"   ✗ Error getting minimum amount: {e}")
        return
    
    # Step 5: Create a payment (commented out for safety)
    print("\nStep 5: Creating a payment...")
    """
    try:
        payment = client.create_payment(
            price_amount=50.00,
            price_currency="usd",
            pay_currency="btc",
            order_id="order_workflow_123",
            order_description="Payment workflow test",
            ipn_callback_url="https://your-site.com/ipn"
        )
        print(f"   ✓ Payment created successfully!")
        print(f"   Payment ID: {payment.payment_id}")
        print(f"   Pay Address: {payment.pay_address}")
        print(f"   Amount to pay: {payment.pay_amount} {payment.pay_currency}")
        print(f"   Status: {payment.payment_status}")
        
        # Step 6: Monitor payment status
        print("\nStep 6: Monitoring payment status...")
        payment_id = payment.payment_id
        
        # Check status a few times
        for i in range(3):
            time.sleep(2)  # Wait 2 seconds between checks
            try:
                status = client.get_payment_status(payment_id)
                print(f"   Check {i+1}: Status = {status.payment_status}")
                
                if status.payment_status == "finished":
                    print(f"   ✓ Payment completed!")
                    print(f"   Actually paid: {status.actually_paid} {status.pay_currency}")
                    break
                elif status.payment_status == "failed":
                    print(f"   ✗ Payment failed")
                    break
                    
            except Exception as e:
                print(f"   ✗ Error checking status: {e}")
                break
                
    except Exception as e:
        print(f"   ✗ Error creating payment: {e}")
    """
    print("   (Payment creation and monitoring commented out for safety)")
    
    # Step 7: IPN verification example
    print("\nStep 7: IPN verification example...")
    try:
        # Initialize IPN verifier
        verifier = IPNVerifier(ipn_secret="YOUR_IPN_SECRET_HERE")
        
        # Example IPN data (this would come from NOWPayments)
        example_ipn_data = {
            "payment_id": 123456789,
            "payment_status": "finished",
            "pay_address": "example_address",
            "price_amount": 50.00,
            "price_currency": "usd",
            "pay_amount": 0.001,
            "pay_currency": "btc"
        }
        
        # Example signature (this would come in the X-NOWPAYMENTS-Sig header)
        example_signature = "example_signature_hash"
        
        # Verify the signature
        is_valid = verifier.verify_signature(example_ipn_data, example_signature)
        print(f"   ✓ IPN verification example: {'Valid' if is_valid else 'Invalid'}")
        
    except Exception as e:
        print(f"   ✗ Error with IPN verification: {e}")
    
    print("\n=== Payment workflow example completed ===")

def subscription_example():
    """Demonstrate subscription functionality."""
    
    print("\n=== Subscription Example ===\n")
    
    # Create a subscription plan
    print("Creating a subscription plan...")
    """
    try:
        plan = client.create_subscription_plan(
            title="Monthly Premium Plan",
            interval_day=30,
            amount=29.99,
            currency="usd",
            ipn_callback_url="https://your-site.com/subscription-ipn"
        )
        print(f"   ✓ Plan created: {plan.title}")
        print(f"   Plan ID: {plan.id}")
        print(f"   Amount: {plan.amount} {plan.currency}")
        print(f"   Interval: {plan.interval_day} days")
        
        # Create a subscription
        print("\nCreating a subscription...")
        subscription = client.create_subscription(
            plan_id=plan.id,
            email="customer@example.com",
            order_id="sub_123",
            order_description="Premium subscription"
        )
        print(f"   ✓ Subscription created: {subscription.subscription_id}")
        print(f"   Email: {subscription.email}")
        print(f"   Status: {subscription.status}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    """
    print("   (Subscription creation commented out for safety)")

def custody_example():
    """Demonstrate custody/sub-account functionality."""
    
    print("\n=== Custody Example ===\n")
    
    # Create a user account
    print("Creating a user account...")
    """
    try:
        user = client.create_user_account(
            external_id="user_123",
            email="user@example.com"
        )
        print(f"   ✓ User account created: {user.user_id}")
        print(f"   External ID: {user.external_id}")
        
        # Create a payment for the user
        print("\nCreating a payment for the user...")
        payment = client.create_user_payment(
            user_id=user.user_id,
            currency="btc",
            amount=0.001
        )
        print(f"   ✓ Payment created: {payment.payment_id}")
        print(f"   Pay address: {payment.pay_address}")
        
        # Get user balance
        print("\nGetting user balance...")
        balance = client.get_user_balance(user.user_id)
        print(f"   ✓ User balance retrieved")
        print(f"   Balance: {balance.balance}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    """
    print("   (Custody operations commented out for safety)")

if __name__ == "__main__":
    payment_workflow_example()
    subscription_example()
    custody_example() 