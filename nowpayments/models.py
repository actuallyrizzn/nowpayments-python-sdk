"""
Data models for the NOWPayments SDK.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


@dataclass
class Currency:
    """Currency information."""
    currency: str
    name: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    enabled: bool = True
    networks: List[str] = field(default_factory=list)


@dataclass
class Estimate:
    """Price estimation result."""
    amount_from: Decimal
    currency_from: str
    currency_to: str
    estimated_amount: Decimal


@dataclass
class Payment:
    """Payment information."""
    payment_id: int
    payment_status: str
    pay_address: str
    price_amount: Decimal
    price_currency: str
    pay_amount: Decimal
    pay_currency: str
    order_id: Optional[str] = None
    order_description: Optional[str] = None
    purchase_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    outcome_amount: Optional[Decimal] = None
    outcome_currency: Optional[str] = None
    actually_paid: Optional[Decimal] = None
    commission_fee: Optional[Decimal] = None
    payin_extra_id: Optional[str] = None
    ipn_callback_url: Optional[str] = None
    payout_address: Optional[str] = None
    payout_currency: Optional[str] = None
    external_id: Optional[str] = None
    expire_at: Optional[datetime] = None


@dataclass
class PaymentStatus:
    """Payment status information."""
    payment_id: int
    payment_status: str
    pay_address: str
    price_amount: Decimal
    price_currency: str
    pay_amount: Decimal
    pay_currency: str
    order_id: Optional[str] = None
    order_description: Optional[str] = None
    purchase_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    outcome_amount: Optional[Decimal] = None
    outcome_currency: Optional[str] = None
    actually_paid: Optional[Decimal] = None
    commission_fee: Optional[Decimal] = None
    payin_extra_id: Optional[str] = None


@dataclass
class Invoice:
    """Invoice information."""
    invoice_id: str
    invoice_url: str
    order_id: str
    price_amount: Decimal
    price_currency: str
    invoice_status: str
    pay_currency: Optional[str] = None
    pay_amount: Optional[Decimal] = None
    payment_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SubscriptionPlan:
    """Subscription plan information."""
    id: str
    title: str
    interval_day: int
    amount: Decimal
    currency: str
    ipn_callback_url: Optional[str] = None
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    partially_paid_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Subscription information."""
    subscription_id: str
    plan_id: str
    email: str
    status: str
    order_id: Optional[str] = None
    order_description: Optional[str] = None
    next_payment_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_payment_date: Optional[datetime] = None
    last_payment: Optional[Dict[str, Any]] = None


@dataclass
class PayoutWithdrawal:
    """Individual payout withdrawal."""
    id: str
    address: str
    currency: str
    amount: Decimal
    status: str
    ipn_callback_url: Optional[str] = None
    fiat_amount: Optional[Decimal] = None
    fiat_currency: Optional[str] = None
    txid: Optional[str] = None
    finished_at: Optional[datetime] = None


@dataclass
class PayoutBatch:
    """Payout batch information."""
    batch_id: str
    status: str
    withdrawals: List[PayoutWithdrawal]
    total_amount: Optional[Decimal] = None
    total_currency: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    ipn_callback_url: Optional[str] = None


@dataclass
class UserAccount:
    """User account (sub-account) information."""
    user_id: int
    external_id: Optional[str] = None
    email: Optional[str] = None
    balance: List[Dict[str, Any]] = field(default_factory=list)
    created_at: Optional[datetime] = None


@dataclass
class Transfer:
    """Transfer information."""
    transfer_id: str
    from_id: int
    to_id: int
    currency: str
    amount: Decimal
    status: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Conversion:
    """Currency conversion information."""
    conversion_id: str
    from_currency: str
    to_currency: str
    from_amount: Decimal
    to_amount: Decimal
    status: str
    rate: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AddressValidation:
    """Address validation result."""
    address: str
    currency: str
    result: bool
    message: str
    extra_id: Optional[str] = None 