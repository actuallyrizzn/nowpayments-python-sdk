# Live Tests Setup Guide

This guide explains how to set up and run live tests for the NOWPayments Python SDK.

## 🔐 Security First

The live tests use environment variables to securely manage API credentials. **Never commit your actual API keys to version control.**

## 📋 Prerequisites

1. **NOWPayments Account**: You need a NOWPayments account with API access
2. **API Credentials**: Your API key and other credentials from the NOWPayments dashboard
3. **Python Environment**: The SDK and its dependencies installed

## 🚀 Quick Setup

### Step 1: Copy Environment Template

```bash
# Copy the environment template
cp tests/env.example tests/.env
```

### Step 2: Configure Your Credentials

Edit `tests/.env` and fill in your actual credentials:

```bash
# Edit the .env file with your credentials
# You can use any text editor
notepad tests/.env  # Windows
# or
nano tests/.env     # Linux/Mac
```

### Step 3: Fill in Your Credentials

Replace the placeholder values in `tests/.env`:

```env
# API Key (required)
NOWPAYMENTS_API_KEY=your_actual_api_key_here

# IPN Secret (for IPN verification tests)
NOWPAYMENTS_IPN_SECRET=your_actual_ipn_secret_here

# JWT Token (for 2FA tests)
NOWPAYMENTS_JWT_TOKEN=your_actual_jwt_token_here

# OTP Code (for 2FA tests)
NOWPAYMENTS_OTP_CODE=123456

# Environment (sandbox or production)
NOWPAYMENTS_ENVIRONMENT=sandbox

# Optional: Custom base URL for testing
# NOWPAYMENTS_BASE_URL=https://api.nowpayments.io
```

## 🧪 Running Live Tests

### Basic Usage

```bash
# Run all live tests (sandbox)
python run_live_tests.py

# Run with verbose output
python run_live_tests.py --verbose

# Run specific test
python run_live_tests.py --test test_live_api_status

# Run multiple specific tests
python run_live_tests.py --test "test_live_api_status or test_live_get_currencies"
```

### Advanced Usage

```bash
# Override API key from command line
python run_live_tests.py --api-key YOUR_API_KEY

# Run in production (use with caution)
python run_live_tests.py --production

# Run with custom environment
NOWPAYMENTS_ENVIRONMENT=production python run_live_tests.py
```

## 🔒 Security Features

### Environment Variable Management

- **Secure Storage**: Credentials stored in `.env` files (not in code)
- **Git Ignored**: `.env` files are automatically ignored by Git
- **Template Provided**: `tests/env.example` shows required variables
- **Flexible Override**: Command line arguments can override `.env` values

### Environment Safety

- **Sandbox Default**: Tests run in sandbox environment by default
- **Production Warning**: Explicit confirmation required for production
- **Graceful Failures**: Tests skip if credentials are missing
- **Rate Limiting**: Built-in protection against API rate limits

## 📊 Available Live Tests

### Core API Tests
- `test_live_api_status` - API connectivity
- `test_live_get_currencies` - Available currencies
- `test_live_get_full_currencies` - Detailed currency info
- `test_live_get_merchant_currencies` - Merchant-specific currencies

### Payment Tests
- `test_live_create_payment` - Create payments
- `test_live_get_payment_status` - Check payment status
- `test_live_list_payments` - List all payments
- `test_live_estimate_payment` - Payment estimation

### Invoice Tests
- `test_live_create_invoice` - Create invoices
- `test_live_get_invoice_status` - Check invoice status

### Subscription Tests
- `test_live_create_subscription_plan` - Create subscription plans
- `test_live_get_subscription_plan` - Get plan details
- `test_live_list_subscription_plans` - List all plans
- `test_live_create_subscription` - Create subscriptions
- `test_live_get_subscription` - Get subscription details
- `test_live_list_subscriptions` - List all subscriptions

### Utility Tests
- `test_live_validate_address` - Address validation
- `test_live_get_min_amount` - Minimum payment amounts
- `test_live_get_balance` - Account balance
- `test_live_list_conversions` - Currency conversions

### Security Tests
- `test_live_ipn_verification` - IPN signature verification
- `test_live_error_handling` - Error handling scenarios
- `test_live_rate_limiting` - Rate limiting behavior

### Workflow Tests
- `test_live_comprehensive_workflow` - Complete payment workflow
- `test_live_create_user_account` - User account management
- `test_live_get_user_account` - User account details
- `test_live_list_user_accounts` - List user accounts

## 🛠️ Troubleshooting

### Common Issues

#### 1. "No .env file found"
```bash
# Solution: Create the .env file
cp tests/env.example tests/.env
# Then edit tests/.env with your credentials
```

#### 2. "NOWPAYMENTS_API_KEY not found"
```bash
# Solution: Add your API key to tests/.env
echo "NOWPAYMENTS_API_KEY=your_key_here" >> tests/.env
```

#### 3. Tests being skipped
```bash
# This is normal if credentials are missing or API is unavailable
# Check your .env file and API connectivity
```

#### 4. Production environment warning
```bash
# This is a safety feature
# Type 'y' to continue or 'n' to abort
```

### Debug Mode

```bash
# Run with maximum verbosity
python run_live_tests.py --verbose --test test_live_api_status

# Check environment variables
python -c "import os; print('API_KEY:', os.getenv('NOWPAYMENTS_API_KEY'))"
```

## 📝 Best Practices

### For Development
1. **Use Sandbox**: Always test in sandbox environment first
2. **Small Amounts**: Use small payment amounts for testing
3. **Clean Data**: Use unique order IDs to avoid conflicts
4. **Monitor Logs**: Check test output for any issues

### For Production
1. **Verify Credentials**: Double-check all API credentials
2. **Test Thoroughly**: Run all tests before production deployment
3. **Monitor Rate Limits**: Be aware of API rate limits
4. **Backup Data**: Keep backups of important test data

### Security Checklist
- [ ] `.env` file is in `.gitignore`
- [ ] No credentials in code or documentation
- [ ] Using sandbox environment for testing
- [ ] API keys have appropriate permissions
- [ ] IP whitelisting configured if needed

## 🔄 Continuous Integration

For CI/CD pipelines, set environment variables securely:

```yaml
# GitHub Actions example
env:
  NOWPAYMENTS_API_KEY: ${{ secrets.NOWPAYMENTS_API_KEY }}
  NOWPAYMENTS_ENVIRONMENT: sandbox
```

## 📞 Support

If you encounter issues with live tests:

1. **Check Credentials**: Verify your API credentials are correct
2. **Check Environment**: Ensure you're using the right environment (sandbox/production)
3. **Check Network**: Verify internet connectivity and API access
4. **Check Logs**: Review test output for specific error messages

For SDK-specific issues, check the main documentation or create an issue in the repository. 