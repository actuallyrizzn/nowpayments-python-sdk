"""
Main NOWPayments client for interacting with the API.
"""

import json
import time
import decimal
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode

import requests

from .exceptions import (
    NOWPaymentsError,
    AuthenticationError,
    PaymentError,
    PayoutError,
    SubscriptionError,
    CustodyError,
    ConversionError,
    ValidationError,
    RateLimitError,
)
from .models import (
    Payment,
    PaymentStatus,
    Invoice,
    Subscription,
    SubscriptionPlan,
    PayoutBatch,
    PayoutWithdrawal,
    UserAccount,
    Transfer,
    Conversion,
    Currency,
    Estimate,
    AddressValidation,
)


class NOWPayments:
    """Main client for interacting with the NOWPayments API."""
    
    def __init__(
        self,
        api_key: str,
        sandbox: bool = False,
        timeout: int = 30,
        retries: int = 3,
        base_url: Optional[str] = None
    ):
        """
        Initialize the NOWPayments client.
        
        Args:
            api_key: Your NOWPayments API key
            sandbox: Whether to use sandbox environment
            timeout: Request timeout in seconds
            retries: Number of retries for failed requests
            base_url: Custom base URL (for testing)
        """
        self.api_key = api_key
        self.sandbox = sandbox
        self.timeout = timeout
        self.retries = retries
        
        if base_url:
            self.base_url = base_url
        elif sandbox:
            self.base_url = "https://api-sandbox.nowpayments.io/v1"
        else:
            self.base_url = "https://api.nowpayments.io/v1"
        
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'NOWPayments-Python-SDK/1.0.0'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the NOWPayments API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            API response data
            
        Raises:
            NOWPaymentsError: For API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        if headers:
            request_headers = self.session.headers.copy()
            request_headers.update(headers)
        else:
            request_headers = self.session.headers
        
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    if attempt < self.retries:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise RateLimitError("Rate limit exceeded")
                
                # For 5xx errors, retry
                if response.status_code >= 500:
                    if attempt < self.retries:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('message', f"HTTP {response.status_code}")
                    
                    if response.status_code == 401:
                        raise AuthenticationError(error_msg, response.status_code, error_data)
                    elif response.status_code == 422:
                        raise ValidationError(error_msg, response.status_code, error_data)
                    elif response.status_code == 429:
                        raise RateLimitError(error_msg, response.status_code, error_data)
                    elif '/payment' in endpoint:
                        raise PaymentError(error_msg, response.status_code, error_data)
                    elif '/payout' in endpoint:
                        raise PayoutError(error_msg, response.status_code, error_data)
                    elif '/subscription' in endpoint:
                        raise SubscriptionError(error_msg, response.status_code, error_data)
                    elif '/custody' in endpoint:
                        raise CustodyError(error_msg, response.status_code, error_data)
                    elif '/conversion' in endpoint:
                        raise ConversionError(error_msg, response.status_code, error_data)
                    else:
                        raise NOWPaymentsError(error_msg, response.status_code, error_data)
                
                return response.json() if response.content else {}
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retries:
                    raise NOWPaymentsError(f"Request failed: {str(e)}")
                time.sleep(2 ** attempt)
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse decimal value from API."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None
    
    # General endpoints
    
    def get_status(self) -> Dict[str, str]:
        """Check API status."""
        return self._make_request('GET', '/status')
    
    def get_currencies(self) -> List[str]:
        """Get available currencies."""
        response = self._make_request('GET', '/currencies')
        return response.get('currencies', [])
    
    def get_merchant_currencies(self) -> List[str]:
        """Get merchant's active currencies."""
        response = self._make_request('GET', '/merchant/coins')
        return response.get('currencies', [])
    
    def get_full_currencies(self) -> List[Currency]:
        """Get detailed currency information."""
        response = self._make_request('GET', '/full-currencies')
        currencies = []
        for currency_data in response.get('currencies', []):
            currencies.append(Currency(
                currency=currency_data.get('currency'),
                name=currency_data.get('name'),
                min_amount=self._parse_decimal(currency_data.get('min_amount')),
                max_amount=self._parse_decimal(currency_data.get('max_amount')),
                enabled=currency_data.get('enabled', True),
                networks=currency_data.get('networks', [])
            ))
        return currencies
    
    def get_min_amount(self, currency_from: str, currency_to: str) -> Dict[str, Any]:
        """Get minimum payment amount for currency pair."""
        params = {
            'currency_from': currency_from,
            'currency_to': currency_to
        }
        return self._make_request('GET', '/min-amount', params=params)
    
    def get_estimate(
        self,
        amount: Union[float, Decimal],
        currency_from: str,
        currency_to: str
    ) -> Estimate:
        """Get price estimate for currency conversion."""
        params = {
            'amount': str(amount),
            'currency_from': currency_from,
            'currency_to': currency_to
        }
        response = self._make_request('GET', '/estimate', params=params)
        
        return Estimate(
            amount_from=self._parse_decimal(response.get('amount_from')),
            currency_from=response.get('currency_from'),
            currency_to=response.get('currency_to'),
            estimated_amount=self._parse_decimal(response.get('estimated_amount'))
        )
    
    # Payment endpoints
    
    def create_payment(
        self,
        price_amount: Union[float, Decimal],
        price_currency: str,
        pay_currency: str,
        pay_amount: Optional[Union[float, Decimal]] = None,
        ipn_callback_url: Optional[str] = None,
        order_id: Optional[str] = None,
        order_description: Optional[str] = None,
        purchase_id: Optional[str] = None,
        payout_address: Optional[str] = None,
        payout_currency: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Payment:
        """Create a new payment."""
        data = {
            'price_amount': str(price_amount),
            'price_currency': price_currency,
            'pay_currency': pay_currency
        }
        
        if pay_amount is not None:
            data['pay_amount'] = str(pay_amount)
        if ipn_callback_url:
            data['ipn_callback_url'] = ipn_callback_url
        if order_id:
            data['order_id'] = order_id
        if order_description:
            data['order_description'] = order_description
        if purchase_id:
            data['purchase_id'] = purchase_id
        if payout_address:
            data['payout_address'] = payout_address
        if payout_currency:
            data['payout_currency'] = payout_currency
        if external_id:
            data['external_id'] = external_id
        
        response = self._make_request('POST', '/payment', data=data)
        
        return Payment(
            payment_id=response.get('payment_id'),
            payment_status=response.get('payment_status'),
            pay_address=response.get('pay_address'),
            price_amount=self._parse_decimal(response.get('price_amount')),
            price_currency=response.get('price_currency'),
            pay_amount=self._parse_decimal(response.get('pay_amount')),
            pay_currency=response.get('pay_currency'),
            order_id=response.get('order_id'),
            order_description=response.get('order_description'),
            purchase_id=response.get('purchase_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            outcome_amount=self._parse_decimal(response.get('outcome_amount')),
            outcome_currency=response.get('outcome_currency'),
            actually_paid=self._parse_decimal(response.get('actually_paid')),
            commission_fee=self._parse_decimal(response.get('commission_fee')),
            payin_extra_id=response.get('payin_extra_id'),
            ipn_callback_url=response.get('ipn_callback_url'),
            payout_address=response.get('payout_address'),
            payout_currency=response.get('payout_currency'),
            external_id=response.get('external_id'),
            expire_at=self._parse_datetime(response.get('expire_at'))
        )
    
    def get_payment_status(self, payment_id: int) -> PaymentStatus:
        """Get payment status."""
        response = self._make_request('GET', f'/payment/{payment_id}')
        
        return PaymentStatus(
            payment_id=response.get('payment_id'),
            payment_status=response.get('payment_status'),
            pay_address=response.get('pay_address'),
            price_amount=self._parse_decimal(response.get('price_amount')),
            price_currency=response.get('price_currency'),
            pay_amount=self._parse_decimal(response.get('pay_amount')),
            pay_currency=response.get('pay_currency'),
            order_id=response.get('order_id'),
            order_description=response.get('order_description'),
            purchase_id=response.get('purchase_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            outcome_amount=self._parse_decimal(response.get('outcome_amount')),
            outcome_currency=response.get('outcome_currency'),
            actually_paid=self._parse_decimal(response.get('actually_paid')),
            commission_fee=self._parse_decimal(response.get('commission_fee')),
            payin_extra_id=response.get('payin_extra_id')
        )
    
    def list_payments(
        self,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        order_by: Optional[str] = None,
        order: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        payment_status: Optional[str] = None,
        pay_currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """List payments with optional filters."""
        params = {}
        if limit is not None:
            params['limit'] = limit
        if page is not None:
            params['page'] = page
        if order_by:
            params['order_by'] = order_by
        if order:
            params['order'] = order
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if payment_status:
            params['payment_status'] = payment_status
        if pay_currency:
            params['pay_currency'] = pay_currency
        
        return self._make_request('GET', '/payment', params=params)
    
    def update_payment_estimate(self, payment_id: int) -> Payment:
        """Update payment estimate with current rates."""
        response = self._make_request('POST', f'/payment/{payment_id}/update-merchant-estimate')
        
        return Payment(
            payment_id=response.get('payment_id'),
            payment_status=response.get('payment_status'),
            pay_address=response.get('pay_address'),
            price_amount=self._parse_decimal(response.get('price_amount')),
            price_currency=response.get('price_currency'),
            pay_amount=self._parse_decimal(response.get('pay_amount')),
            pay_currency=response.get('pay_currency'),
            order_id=response.get('order_id'),
            order_description=response.get('order_description'),
            purchase_id=response.get('purchase_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            outcome_amount=self._parse_decimal(response.get('outcome_amount')),
            outcome_currency=response.get('outcome_currency'),
            actually_paid=self._parse_decimal(response.get('actually_paid')),
            commission_fee=self._parse_decimal(response.get('commission_fee')),
            payin_extra_id=response.get('payin_extra_id'),
            ipn_callback_url=response.get('ipn_callback_url'),
            payout_address=response.get('payout_address'),
            payout_currency=response.get('payout_currency'),
            external_id=response.get('external_id'),
            expire_at=self._parse_datetime(response.get('expire_at'))
        )
    
    # Invoice endpoints
    
    def create_invoice(
        self,
        price_amount: Union[float, Decimal],
        price_currency: str,
        order_id: str,
        order_description: Optional[str] = None,
        ipn_callback_url: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Invoice:
        """Create a new invoice."""
        data = {
            'price_amount': str(price_amount),
            'price_currency': price_currency,
            'order_id': order_id
        }
        
        if order_description:
            data['order_description'] = order_description
        if ipn_callback_url:
            data['ipn_callback_url'] = ipn_callback_url
        if success_url:
            data['success_url'] = success_url
        if cancel_url:
            data['cancel_url'] = cancel_url
        
        response = self._make_request('POST', '/invoice', data=data)
        
        return Invoice(
            invoice_id=response.get('invoice_id'),
            invoice_url=response.get('invoice_url'),
            order_id=response.get('order_id'),
            price_amount=self._parse_decimal(response.get('price_amount')),
            price_currency=response.get('price_currency'),
            invoice_status=response.get('invoice_status'),
            pay_currency=response.get('pay_currency'),
            pay_amount=self._parse_decimal(response.get('pay_amount')),
            payment_id=response.get('payment_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at'))
        )
    
    def get_invoice_status(self, invoice_id: str) -> Invoice:
        """Get invoice status."""
        response = self._make_request('GET', f'/invoice/{invoice_id}')
        
        return Invoice(
            invoice_id=response.get('invoice_id'),
            invoice_url=response.get('invoice_url'),
            order_id=response.get('order_id'),
            price_amount=self._parse_decimal(response.get('price_amount')),
            price_currency=response.get('price_currency'),
            invoice_status=response.get('invoice_status'),
            pay_currency=response.get('pay_currency'),
            pay_amount=self._parse_decimal(response.get('pay_amount')),
            payment_id=response.get('payment_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at'))
        )
    
    def create_invoice_payment(
        self,
        invoice_id: str,
        pay_currency: str,
        purchase_id: Optional[str] = None,
        order_description: Optional[str] = None,
        customer_email: Optional[str] = None,
        payout_address: Optional[str] = None,
        payout_extra_id: Optional[str] = None,
        payout_currency: Optional[str] = None
    ) -> Payment:
        """Create a payment for an existing invoice."""
        data = {
            'iid': invoice_id,
            'pay_currency': pay_currency
        }
        
        if purchase_id:
            data['purchase_id'] = purchase_id
        if order_description:
            data['order_description'] = order_description
        if customer_email:
            data['customer_email'] = customer_email
        if payout_address:
            data['payout_address'] = payout_address
        if payout_extra_id:
            data['payout_extra_id'] = payout_extra_id
        if payout_currency:
            data['payout_currency'] = payout_currency
        
        response = self._make_request('POST', '/invoice-payment', data=data)
        
        return Payment(
            payment_id=response.get('payment_id'),
            payment_status=response.get('payment_status'),
            pay_address=response.get('pay_address'),
            price_amount=self._parse_decimal(response.get('price_amount')),
            price_currency=response.get('price_currency'),
            pay_amount=self._parse_decimal(response.get('pay_amount')),
            pay_currency=response.get('pay_currency'),
            order_id=response.get('order_id'),
            order_description=response.get('order_description'),
            purchase_id=response.get('purchase_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            outcome_amount=self._parse_decimal(response.get('outcome_amount')),
            outcome_currency=response.get('outcome_currency'),
            actually_paid=self._parse_decimal(response.get('actually_paid')),
            commission_fee=self._parse_decimal(response.get('commission_fee')),
            payin_extra_id=response.get('payin_extra_id'),
            ipn_callback_url=response.get('ipn_callback_url'),
            payout_address=response.get('payout_address'),
            payout_currency=response.get('payout_currency'),
            external_id=response.get('external_id'),
            expire_at=self._parse_datetime(response.get('expire_at'))
        )
    
    # Subscription endpoints
    
    def create_subscription_plan(
        self,
        title: str,
        interval_day: int,
        amount: Union[float, Decimal],
        currency: str,
        ipn_callback_url: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        partially_paid_url: Optional[str] = None
    ) -> SubscriptionPlan:
        """Create a subscription plan."""
        data = {
            'title': title,
            'interval_day': interval_day,
            'amount': str(amount),
            'currency': currency
        }
        
        if ipn_callback_url:
            data['ipn_callback_url'] = ipn_callback_url
        if success_url:
            data['success_url'] = success_url
        if cancel_url:
            data['cancel_url'] = cancel_url
        if partially_paid_url:
            data['partially_paid_url'] = partially_paid_url
        
        response = self._make_request('POST', '/subscriptions/plans', data=data)
        result = response.get('result', response)

        return SubscriptionPlan(
            id=result.get('id') or result.get('plan_id'),
            title=result.get('title'),
            interval_day=int(result.get('interval_day', 0)),
            amount=self._parse_decimal(result.get('amount')),
            currency=result.get('currency'),
            ipn_callback_url=result.get('ipn_callback_url'),
            success_url=result.get('success_url'),
            cancel_url=result.get('cancel_url'),
            partially_paid_url=result.get('partially_paid_url'),
            created_at=self._parse_datetime(result.get('created_at')),
            updated_at=self._parse_datetime(result.get('updated_at'))
        )
    
    def update_subscription_plan(
        self,
        plan_id: str,
        **kwargs
    ) -> SubscriptionPlan:
        """Update a subscription plan."""
        response = self._make_request('PATCH', f'/subscriptions/plans/{plan_id}', data=kwargs)
        
        return SubscriptionPlan(
            id=response.get('id') or response.get('plan_id'),
            title=response.get('title'),
            interval_day=int(response.get('interval_day', 0)),
            amount=self._parse_decimal(response.get('amount')),
            currency=response.get('currency'),
            ipn_callback_url=response.get('ipn_callback_url'),
            success_url=response.get('success_url'),
            cancel_url=response.get('cancel_url'),
            partially_paid_url=response.get('partially_paid_url'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at'))
        )
    
    def get_subscription_plan(self, plan_id: str) -> SubscriptionPlan:
        """Get subscription plan details."""
        response = self._make_request('GET', f'/subscriptions/plans/{plan_id}')
        
        return SubscriptionPlan(
            id=response.get('id') or response.get('plan_id'),
            title=response.get('title'),
            interval_day=int(response.get('interval_day', 0)),
            amount=self._parse_decimal(response.get('amount')),
            currency=response.get('currency'),
            ipn_callback_url=response.get('ipn_callback_url'),
            success_url=response.get('success_url'),
            cancel_url=response.get('cancel_url'),
            partially_paid_url=response.get('partially_paid_url'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at'))
        )
    
    def list_subscription_plans(self) -> List[SubscriptionPlan]:
        """List all subscription plans."""
        response = self._make_request('GET', '/subscriptions/plans')
        plans = []
        
        for plan_data in response.get('plans', []):
            plans.append(SubscriptionPlan(
                id=plan_data.get('id') or plan_data.get('plan_id'),
                title=plan_data.get('title'),
                interval_day=int(plan_data.get('interval_day', 0)),
                amount=self._parse_decimal(plan_data.get('amount')),
                currency=plan_data.get('currency'),
                ipn_callback_url=plan_data.get('ipn_callback_url'),
                success_url=plan_data.get('success_url'),
                cancel_url=plan_data.get('cancel_url'),
                partially_paid_url=plan_data.get('partially_paid_url'),
                created_at=self._parse_datetime(plan_data.get('created_at')),
                updated_at=self._parse_datetime(plan_data.get('updated_at'))
            ))
        
        return plans
    
    def create_subscription(
        self,
        plan_id: str,
        email: str,
        order_id: Optional[str] = None,
        order_description: Optional[str] = None,
        customer_name: Optional[str] = None,
        starting_day: Optional[int] = None
    ) -> Subscription:
        """Create a subscription."""
        data = {
            'plan_id': plan_id,
            'email': email
        }
        
        if order_id:
            data['order_id'] = order_id
        if order_description:
            data['order_description'] = order_description
        if customer_name:
            data['customer_name'] = customer_name
        if starting_day is not None:
            data['starting_day'] = starting_day
        
        response = self._make_request('POST', '/subscriptions', data=data)
        
        return Subscription(
            subscription_id=response.get('subscription_id'),
            plan_id=response.get('plan_id'),
            email=response.get('email'),
            order_id=response.get('order_id'),
            order_description=response.get('order_description'),
            status=response.get('status'),
            next_payment_date=self._parse_datetime(response.get('next_payment_date')),
            created_at=self._parse_datetime(response.get('created_at')),
            last_payment_date=self._parse_datetime(response.get('last_payment_date')),
            last_payment=response.get('last_payment')
        )
    
    def list_subscriptions(
        self,
        plan_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """List subscriptions with optional filters."""
        params = {}
        if plan_id:
            params['plan_id'] = plan_id
        if status:
            params['status'] = status
        if limit is not None:
            params['limit'] = limit
        if page is not None:
            params['page'] = page
        
        return self._make_request('GET', '/subscriptions', params=params)
    
    def get_subscription(self, subscription_id: str) -> Subscription:
        """Get subscription details."""
        response = self._make_request('GET', f'/subscriptions/{subscription_id}')
        
        return Subscription(
            subscription_id=response.get('subscription_id'),
            plan_id=response.get('plan_id'),
            email=response.get('email'),
            order_id=response.get('order_id'),
            order_description=response.get('order_description'),
            status=response.get('status'),
            next_payment_date=self._parse_datetime(response.get('next_payment_date')),
            created_at=self._parse_datetime(response.get('created_at')),
            last_payment_date=self._parse_datetime(response.get('last_payment_date')),
            last_payment=response.get('last_payment')
        )
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription."""
        try:
            self._make_request('DELETE', f'/subscriptions/{subscription_id}')
            return True
        except NOWPaymentsError:
            return False
    
    # Payout endpoints
    
    def create_payout(
        self,
        withdrawals: List[Dict[str, Any]],
        ipn_callback_url: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> PayoutBatch:
        """Create a payout batch."""
        data = {
            'withdrawals': withdrawals
        }
        
        if ipn_callback_url:
            data['ipn_callback_url'] = ipn_callback_url
        
        headers = {}
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        response = self._make_request('POST', '/payout', data=data, headers=headers)
        
        withdrawals_list = []
        for wd_data in response.get('withdrawals', []):
            withdrawals_list.append(PayoutWithdrawal(
                id=wd_data.get('id'),
                address=wd_data.get('address'),
                currency=wd_data.get('currency'),
                amount=self._parse_decimal(wd_data.get('amount')),
                status=wd_data.get('status'),
                ipn_callback_url=wd_data.get('ipn_callback_url'),
                fiat_amount=self._parse_decimal(wd_data.get('fiat_amount')),
                fiat_currency=wd_data.get('fiat_currency'),
                txid=wd_data.get('txid'),
                finished_at=self._parse_datetime(wd_data.get('finished_at'))
            ))
        
        return PayoutBatch(
            batch_id=response.get('batch_id'),
            status=response.get('status'),
            withdrawals=withdrawals_list,
            total_amount=self._parse_decimal(response.get('total_amount')),
            total_currency=response.get('total_currency'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            verified_at=self._parse_datetime(response.get('verified_at')),
            ipn_callback_url=response.get('ipn_callback_url')
        )
    
    def verify_payout(self, batch_id: str, code: str) -> PayoutBatch:
        """Verify payout with 2FA code."""
        data = {'code': code}
        response = self._make_request('POST', f'/payout/{batch_id}/verify', data=data)
        
        withdrawals_list = []
        for wd_data in response.get('withdrawals', []):
            withdrawals_list.append(PayoutWithdrawal(
                id=wd_data.get('id'),
                address=wd_data.get('address'),
                currency=wd_data.get('currency'),
                amount=self._parse_decimal(wd_data.get('amount')),
                status=wd_data.get('status'),
                ipn_callback_url=wd_data.get('ipn_callback_url'),
                fiat_amount=self._parse_decimal(wd_data.get('fiat_amount')),
                fiat_currency=wd_data.get('fiat_currency'),
                txid=wd_data.get('txid'),
                finished_at=self._parse_datetime(wd_data.get('finished_at'))
            ))
        
        return PayoutBatch(
            batch_id=response.get('batch_id'),
            status=response.get('status'),
            withdrawals=withdrawals_list,
            total_amount=self._parse_decimal(response.get('total_amount')),
            total_currency=response.get('total_currency'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            verified_at=self._parse_datetime(response.get('verified_at')),
            ipn_callback_url=response.get('ipn_callback_url')
        )
    
    def get_payout_status(self, batch_id: str) -> PayoutBatch:
        """Get payout batch status."""
        response = self._make_request('GET', f'/payout/{batch_id}')
        
        withdrawals_list = []
        for wd_data in response.get('withdrawals', []):
            withdrawals_list.append(PayoutWithdrawal(
                id=wd_data.get('id'),
                address=wd_data.get('address'),
                currency=wd_data.get('currency'),
                amount=self._parse_decimal(wd_data.get('amount')),
                status=wd_data.get('status'),
                ipn_callback_url=wd_data.get('ipn_callback_url'),
                fiat_amount=self._parse_decimal(wd_data.get('fiat_amount')),
                fiat_currency=wd_data.get('fiat_currency'),
                txid=wd_data.get('txid'),
                finished_at=self._parse_datetime(wd_data.get('finished_at'))
            ))
        
        return PayoutBatch(
            batch_id=response.get('batch_id'),
            status=response.get('status'),
            withdrawals=withdrawals_list,
            total_amount=self._parse_decimal(response.get('total_amount')),
            total_currency=response.get('total_currency'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at')),
            verified_at=self._parse_datetime(response.get('verified_at')),
            ipn_callback_url=response.get('ipn_callback_url')
        )
    
    def list_payouts(
        self,
        batch_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        order_by: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """List payout batches with optional filters."""
        params = {}
        if batch_id:
            params['batch_id'] = batch_id
        if status:
            params['status'] = status
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        if order_by:
            params['order_by'] = order_by
        if order:
            params['order'] = order
        if limit is not None:
            params['limit'] = limit
        if page is not None:
            params['page'] = page
        
        return self._make_request('GET', '/payout', params=params)
    
    def validate_address(
        self,
        address: str,
        currency: str,
        extra_id: Optional[str] = None
    ) -> AddressValidation:
        """Validate a cryptocurrency address."""
        data = {
            'address': address,
            'currency': currency
        }
        
        if extra_id:
            data['extra_id'] = extra_id
        
        response = self._make_request('POST', '/payout/validate-address', data=data)
        
        return AddressValidation(
            address=response.get('address'),
            currency=response.get('currency'),
            result=response.get('result'),
            message=response.get('message'),
            extra_id=response.get('extra_id')
        )
    
    # Custody endpoints
    
    def create_user_account(
        self,
        external_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> UserAccount:
        """Create a new user account (sub-account)."""
        data = {}
        if external_id:
            data['external_id'] = external_id
        if email:
            data['email'] = email
        
        response = self._make_request('POST', '/sub-partner/balance', data=data)
        
        return UserAccount(
            user_id=response.get('user_id'),
            external_id=response.get('external_id'),
            email=response.get('email'),
            balance=response.get('balance', []),
            created_at=self._parse_datetime(response.get('created_at'))
        )
    
    def get_user_balance(self, user_id: int) -> UserAccount:
        """Get user account balance."""
        response = self._make_request('GET', f'/sub-partner/balance/{user_id}')
        
        return UserAccount(
            user_id=response.get('user_id'),
            external_id=response.get('external_id'),
            email=response.get('email'),
            balance=response.get('balance', []),
            created_at=self._parse_datetime(response.get('created_at'))
        )
    
    def list_user_accounts(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """List user accounts."""
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        if order:
            params['order'] = order
        if order_by:
            params['order_by'] = order_by
        
        return self._make_request('GET', '/sub-partner', params=params)
    
    def create_user_payment(
        self,
        user_id: int,
        currency: str,
        amount: Optional[Union[float, Decimal]] = None,
        track_id: Optional[str] = None
    ) -> Payment:
        """Create a payment for a user account."""
        data = {
            'user_id': user_id,
            'currency': currency
        }
        
        if amount is not None:
            data['amount'] = str(amount)
        if track_id:
            data['track_id'] = track_id
        
        response = self._make_request('POST', '/sub-partner/payment', data=data)
        
        return Payment(
            payment_id=response.get('payment_id'),
            payment_status=response.get('status'),
            pay_address=response.get('pay_address'),
            price_amount=self._parse_decimal(response.get('amount')),
            price_currency=response.get('currency'),
            pay_amount=self._parse_decimal(response.get('amount')),
            pay_currency=response.get('currency'),
            order_id=response.get('track_id'),
            created_at=self._parse_datetime(response.get('created_at')),
            updated_at=self._parse_datetime(response.get('updated_at'))
        )
    
    def transfer_funds(
        self,
        from_id: int,
        to_id: int,
        currency: str,
        amount: Union[float, Decimal]
    ) -> Transfer:
        """Transfer funds between accounts."""
        data = {
            'from_id': from_id,
            'to_id': to_id,
            'currency': currency,
            'amount': str(amount)
        }
        
        response = self._make_request('POST', '/sub-partner/transfer', data=data)
        
        return Transfer(
            transfer_id=response.get('transfer_id'),
            from_id=response.get('from_id'),
            to_id=response.get('to_id'),
            currency=response.get('currency'),
            amount=self._parse_decimal(response.get('amount')),
            status=response.get('status'),
            created_at=self._parse_datetime(response.get('created_at')),
            completed_at=self._parse_datetime(response.get('completed_at'))
        )
    
    def list_transfers(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None
    ) -> Dict[str, Any]:
        """List transfers."""
        params = {}
        if user_id is not None:
            params['id'] = user_id
        if status:
            params['status'] = status
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if order:
            params['order'] = order
        
        return self._make_request('GET', '/sub-partner/transfers', params=params)
    
    def get_transfer(self, transfer_id: str) -> Transfer:
        """Get transfer details."""
        response = self._make_request('GET', f'/sub-partner/transfer/{transfer_id}')
        
        return Transfer(
            transfer_id=response.get('transfer_id'),
            from_id=response.get('from_id'),
            to_id=response.get('to_id'),
            currency=response.get('currency'),
            amount=self._parse_decimal(response.get('amount')),
            status=response.get('status'),
            created_at=self._parse_datetime(response.get('created_at')),
            completed_at=self._parse_datetime(response.get('completed_at'))
        )
    
    def withdraw_funds(
        self,
        user_id: int,
        currency: str,
        amount: Union[float, Decimal],
        address: Optional[str] = None,
        address_extra: Optional[str] = None,
        ipn_callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Withdraw funds from user account."""
        data = {
            'user_id': user_id,
            'currency': currency,
            'amount': str(amount)
        }
        
        if address:
            data['address'] = address
        if address_extra:
            data['address_extra'] = address_extra
        if ipn_callback_url:
            data['ipn_callback_url'] = ipn_callback_url
        
        return self._make_request('POST', '/sub-partner/write-off', data=data)
    
    # Conversion endpoints
    
    def create_conversion(
        self,
        from_currency: str,
        to_currency: str,
        amount: Union[float, Decimal]
    ) -> Conversion:
        """Create a currency conversion."""
        data = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': str(amount)
        }
        
        response = self._make_request('POST', '/conversion', data=data)
        
        return Conversion(
            conversion_id=response.get('conversion_id'),
            from_currency=response.get('from_currency'),
            to_currency=response.get('to_currency'),
            from_amount=self._parse_decimal(response.get('from_amount')),
            to_amount=self._parse_decimal(response.get('to_amount')),
            status=response.get('status'),
            rate=self._parse_decimal(response.get('rate')),
            created_at=self._parse_datetime(response.get('created_at')),
            completed_at=self._parse_datetime(response.get('completed_at'))
        )
    
    def get_conversion_status(self, conversion_id: str) -> Conversion:
        """Get conversion status."""
        response = self._make_request('GET', f'/conversion/{conversion_id}')
        
        return Conversion(
            conversion_id=response.get('conversion_id'),
            from_currency=response.get('from_currency'),
            to_currency=response.get('to_currency'),
            from_amount=self._parse_decimal(response.get('from_amount')),
            to_amount=self._parse_decimal(response.get('to_amount')),
            status=response.get('status'),
            rate=self._parse_decimal(response.get('rate')),
            created_at=self._parse_datetime(response.get('created_at')),
            completed_at=self._parse_datetime(response.get('completed_at'))
        )
    
    def list_conversions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """List conversions."""
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        
        return self._make_request('GET', '/conversion', params=params) 