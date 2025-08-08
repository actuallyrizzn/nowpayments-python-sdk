Understood. I’ll produce a fully exhaustive NowPayments API reference using only publicly documented endpoints, complete with cURL request examples, output samples, and arguments in one unified document.

I’ll get started on this and let you know when it’s ready to review.


# NOWPayments API Reference

## Authentication & API Access

All requests to the NOWPayments API must include your API key in the header. Use the header `x-api-key` with your API key value for authentication. The base URL for the API is `https://api.nowpayments.io/v1/`. For example:

```http
x-api-key: YOUR_API_KEY_HERE
```

* **API Key:** Obtain your API key by signing up and generating one in your NOWPayments account. Keep it secret and include it in every request header.
* **Content Type:** For endpoints that require a request body (POST/PATCH), send JSON and include `Content-Type: application/json` in headers.
* **IP Whitelisting:** Certain sensitive operations (e.g. Custody APIs, Payouts) require that the request originates from a whitelisted IP address. Ensure you have added your server’s IP in the NOWPayments dashboard under Security settings.
* **Two-Factor Authorization (2FA):** Payout endpoints require 2FA confirmation. You will need to verify a payout using a one-time 2FA code (see Payouts section). The API allows up to 10 attempts to verify a payout with the correct 2FA code.
* **Sandbox Environment:** A Sandbox base URL (`api-sandbox.nowpayments.io`) is available for testing API calls without real transactions. Use your sandbox API key in that environment.

## General Endpoints (Status & Currencies)

### Check API Status

**Endpoint:** `GET /status`
Checks if the API is up and running normally.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/status" \
     -H "x-api-key: YOUR_API_KEY"
```

**Response:** On success, returns HTTP 200 with a message indicating the API status (e.g. `{"message": "OK"}`).

### Get Available Currencies

**Endpoint:** `GET /currencies`
Returns a list of all cryptocurrency tickers currently available for payments.

* **Authentication:** Requires API key header.
* **Response Format:** JSON with an array of currency codes under the `currencies` field.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/currencies" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "currencies": [
    "btc",
    "eth",
    "xmr",
    "trx",
    "usdttrc20",
    "usdc",
    "... (many more)"
  ]
}
```

### Get Merchant Active Currencies

**Endpoint:** `GET /merchant/coins`
Returns information about the cryptocurrencies that **you have activated** in your NOWPayments account (your enabled coins for acceptance). This is useful for displaying only the coins you support to your users.

* **Authentication:** Requires API key.
* **Response:** JSON list of active currency tickers (and possibly additional info such as coin name or network, if provided).

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/merchant/coins" \
     -H "x-api-key: YOUR_API_KEY"
```

**Response:** (example)

```json
{
  "currencies": [
    "btc",
    "ltc",
    "eth",
    "usdttrc20"
  ]
}
```

### Get Full Currency Details

**Endpoint:** `GET /full-currencies`
Provides detailed information for all available cryptocurrencies. Details include information such as currency ticker, name, minimal payment amounts, and other relevant data for each supported coin.

* **Authentication:** Requires API key.
* **Response:** JSON array of objects, each describing a currency in detail. For example, each object may include:

  * `currency`: the coin ticker (e.g. `"btc"`).
  * `min_amount`: minimum payment amount for this coin (in its own units), etc.
    *(The exact fields returned for each currency are defined by the API and may include additional metadata like network or confirmation counts.)*

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/full-currencies" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
[
  {
    "currency": "btc",
    "name": "Bitcoin",
    "min_amount": 0.0000543,
    "max_amount": null,
    "enabled": true,
    "networks": ["BTC"]
  },
  {
    "currency": "eth",
    "name": "Ethereum",
    "min_amount": 0.0012,
    "max_amount": null,
    "enabled": true,
    "networks": ["ETH"]
  },
  ... 
]
```

*(Fields like `enabled`, `networks`, etc., are indicative – refer to the actual API response for complete details.)*

### Get Minimum Payment Amount

**Endpoint:** `GET /min-amount?currency_from={X}&currency_to={Y}`
Calculates the minimum transferable amount for a given payment currency pair. This is typically used to ensure that a customer does not attempt to pay less than the smallest allowed amount (which could fail due to network fees or other limits).

* **Query Parameters:**

  * `currency_from` – **required**. The cryptocurrency ticker the customer will pay in (e.g. `btc`, `eth`).
  * `currency_to` – **required**. The currency of your payout wallet (the coin you ultimately receive). This is usually a crypto ticker or fiat if converting to fiat in Custody (e.g. `usd` for fiat or a crypto ticker).
* **Response:** JSON with `currency_from`, `currency_to`, and the calculated `min_amount` that must be paid at minimum.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/min-amount?currency_from=eth&currency_to=trx" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "currency_from": "eth",
  "currency_to": "trx",
  "min_amount": 0.0098927
}
```

*(In the above example, the minimum amount of ETH required to be converted to TRX is `0.0098927 ETH`.)*

### Get Estimated Price (Conversion Estimate)

**Endpoint:** `GET /estimate?amount={value}&currency_from={X}&currency_to={Y}`
Calculates an estimate of the target cryptocurrency amount for a given source amount and currency pair. In other words, this endpoint tells you how much of `currency_to` you would receive for a specified amount of `currency_from`, based on current exchange rates.

* **Query Parameters:**

  * `amount` – **required**. The amount of the source currency to convert (as a decimal). This should be expressed in the `currency_from` units (if `currency_from` is fiat, this is a fiat amount; if crypto, a crypto amount).
  * `currency_from` – **required**. The currency ticker of the amount you have (e.g. a fiat currency like `USD` or a crypto like `btc`).
  * `currency_to` – **required**. The currency ticker of the asset you want to estimate the amount in (e.g. the crypto you want to receive).
* **Response:** JSON containing the original parameters and the `estimated_amount` of `currency_to` that corresponds to the input amount.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/estimate?amount=3999.5&currency_from=usd&currency_to=btc" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "amount_from": 3999.5,
  "currency_from": "usd",
  "currency_to": "btc",
  "estimated_amount": 0.17061637
}
```

This indicates that 3999.5 USD is estimated to be worth `0.17061637 BTC` at current rates. Always check that the estimated crypto amount is above the minimum required amount for the currency pair (as given by the **Minimum Payment Amount** endpoint).

## Payments API

The Payments API allows you to create and manage payment requests (crypto invoices) for customers. A typical e-commerce flow is: check API status, get available currencies, calculate minimum amount and estimated price, then create a payment for the customer, and finally monitor the payment status. Below are the endpoints for payments:

### Create Payment (Invoice)

Creates a new payment request for a customer. This generates a unique payment invoice with a deposit address or payment link that your customer will use to send cryptocurrency. Each payment has a unique `payment_id` and associated status.

**Endpoint:** `POST /payment`

**Required Parameters (JSON body):**

* **price\_amount** (decimal) – **Required.** The price of the item or order in fiat currency. This is the amount you want to charge in fiat terms (e.g. `100.00` if price\_currency is USD means \$100.00).
* **price\_currency** (string) – **Required.** The fiat currency code for the price\_amount, e.g. `"usd"`, `"eur"`. This is the currency your price\_amount is denominated in.
* **pay\_currency** (string) – **Required.** The cryptocurrency ticker that the customer will pay in (e.g. `"btc"`, `"eth"`, etc.). The customer will be shown an amount in this cryptocurrency to pay.

**Optional Parameters:**

* **pay\_amount** (decimal) – The exact amount in cryptocurrency to be paid by the customer. If you specify this, the API will use this crypto amount instead of calculating one from price\_amount. If not provided, NOWPayments will calculate the crypto amount based on price\_amount and current rate (internally using the Estimated Price endpoint).
* **ipn\_callback\_url** (string) – URL for Instant Payment Notification callbacks. If set, NOWPayments will send HTTP POST updates to this URL when the payment status changes (see **IPN** below).
* **order\_id** (string) – A custom order identifier from your system (e.g. invoice number or cart ID). This is returned in status updates, allowing you to match payments to your internal orders.
* **order\_description** (string) – Description of the order or item (e.g. `"Apple Macbook Pro 2019 x 1"`). This can be useful for your records or in IPN data.
* **purchase\_id** (string) – An additional custom payment identifier used for grouping payments. If you plan to allow the customer to pay an order in multiple transactions, set a unique `purchase_id` for that order on all related payments. Payments sharing a purchase\_id can be treated as part of the same order for partial payment handling.
* **payout\_address** (string) – (Optional) Override the default outcome wallet address for this payment. By default, payments are sent to the wallet address you set in your NOWPayments account. If you want this specific payment to be delivered to a different address, you can specify it here.
* **payout\_currency** (string) – (Optional) If you want to override the outcome currency for this transaction, specify it here. For example, you might accept payment in one crypto but want the payout in another crypto. The payout currency must be one of your configured outcome currencies. If not set, the payout will be made in whatever currency corresponds to the pay\_currency (or the auto-converted equivalent as per your account settings).
* **external\_id** (string) – (Optional) An external identifier you can assign (for example, to map to a user ID or any entity on your side). This is not used by NOWPayments except to pass it back in callbacks or queries.

(*Note:* There are additional optional fields available in the API; the above are commonly used ones. Refer to the official documentation for a full list.)

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/payment" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "price_amount": 3999.5,
           "price_currency": "usd",
           "pay_currency": "btc",
           "ipn_callback_url": "https://example.com/ipn",
           "order_id": "RGDBP-21314",
           "order_description": "Apple Macbook Pro 2019 x 1"
         }'
```

In this example, we request a payment of \$3999.50 (USD) to be paid by the customer in Bitcoin. We included an IPN callback URL for status notifications and an internal order ID/description.

**Example Response:**

On success, the API returns a JSON object with details of the created payment:

```json
{
  "payment_id": 5524759814,
  "payment_status": "waiting",
  "pay_address": "TNDFkiSmBQorNFacb3735q8MnT29sn8BLn",
  "price_amount": 3999.5,
  "price_currency": "usd",
  "pay_amount": 165.652609,
  "pay_currency": "btc",
  "order_id": "RGDBP-21314",
  "order_description": "Apple Macbook Pro 2019 x 1",
  "purchase_id": "4944856743",
  "created_at": "2025-08-07T16:32:10.123Z",
  "updated_at": "2025-08-07T16:32:10.123Z",
  "outcome_amount": 178.9005,
  "outcome_currency": "trx"
}
```

Key fields to note in the response:

* `payment_id` is the unique identifier for this payment.
* `payment_status` will initially be `"waiting"` (waiting for the customer to pay).
* `pay_address` is the crypto address (or payment wallet) where the customer should send the payment.
* `pay_amount` is the exact amount in cryptocurrency the customer should send (here \~165.652609 TRX or BTC in our example).
* `outcome_amount` and `outcome_currency` indicate the amount and currency that will be delivered to your wallet after payment (for example, NOWPayments can auto-convert the incoming BTC to another coin like TRX as shown above).

The `payment_id` is used to query the payment status in subsequent calls.

### Payment Status & IPN

Once a payment is created, you need to monitor its status to know when it’s paid and confirmed. There are two ways to track payment status:

1. **Query Payment Status Manually** via the API.
2. **Instant Payment Notification (IPN)** callbacks to your server.

#### Get Payment Status

**Endpoint:** `GET /payment/{payment_id}`

Retrieves the latest status and details of a specific payment by its `payment_id`. Use this to poll for status updates if not using IPN.

* **URL Parameter:** `payment_id` – The ID of the payment you want to check (as returned when creating the payment).
* **Authentication:** API key required.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/payment/5524759814" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "payment_id": 5524759814,
  "payment_status": "finished",
  "pay_address": "TNDFkiSmBQorNFacb3735q8MnT29sn8BLn",
  "price_amount": 3999.5,
  "price_currency": "usd",
  "pay_amount": 165.652609,
  "pay_currency": "btc",
  "order_id": "RGDBP-21314",
  "order_description": "Apple Macbook Pro 2019 x 1",
  "purchase_id": "4944856743",
  "created_at": "2025-08-07T16:32:10.123Z",
  "updated_at": "2025-08-07T16:40:22.467Z",
  "outcome_amount": 178.9005,
  "outcome_currency": "trx",
  "actually_paid": 165.652609,
  "commission_fee": 0.5,
  "payin_extra_id": null
}
```

In this example, the payment status is `"finished"`, indicating the payment was completed successfully. The `actually_paid` field shows how much was actually received (in crypto) – it may equal `pay_amount` or be less for partial payments. Possible `payment_status` values include:

* `waiting` – awaiting payment from the customer,
* `confirming` – payment received and awaiting blockchain confirmations,
* `confirmed` – payment confirmed on the blockchain,
* `partially_paid` – customer paid an amount but less than expected (payment incomplete),
* `finished` – payment completed and funds delivered to you,
* `failed` – payment failed (e.g. customer sent an unsupported coin or an error occurred),
* `refunded` – payment was refunded to the payer,
* `expired` – customer did not pay within the allowed time window.

#### Instant Payment Notifications (IPN)

Instead of polling the payment status, you can use IPN callbacks. If you provided an `ipn_callback_url` when creating the payment, NOWPayments will send an HTTP POST to that URL whenever the payment status changes.

* The IPN POST request will contain a JSON body identical to the response of Get Payment Status. It includes all payment fields (like payment\_id, status, amounts, etc.).
* An `X-NOWPAYMENTS-Sig` header will accompany the request. This is an HMAC-SHA512 signature of the JSON body, using your IPN secret key (from your Dashboard). You should verify this signature to ensure the callback is from NOWPayments:

  * To verify, compute HMAC-SHA512 of the JSON payload (with keys sorted) using your IPN secret, and compare it to the `X-NOWPAYMENTS-Sig` header.
* Respond with HTTP 200 OK from your server to acknowledge receipt. If NOWPayments does not receive a 200, it will retry the notification (with exponential backoff, up to a configured number of attempts).

**IPN Example:** If a payment status changes to `waiting` or `confirmed`, you might receive a payload like:

```json
{
  "payment_id": 5077125051,
  "payment_status": "waiting",
  "pay_address": "0xd1cDE08A07cD25adEbEd35c3867a59228C09B606",
  "price_amount": 170,
  "price_currency": "usd",
  "pay_amount": 155.38559757,
  "actually_paid": 0,
  "pay_currency": "mana",
  "order_id": "2",
  "order_description": "Apple Macbook Pro 2019 x 1",
  "purchase_id": "6084744717",
  "created_at": "2021-04-12T14:22:54.942Z",
  "updated_at": "2021-04-12T14:23:06.244Z",
  "outcome_amount": 1131.7812095,
  "outcome_currency": "trx"
}
```

This would be sent to your IPN URL. You would verify the signature and then update your order status accordingly (e.g. mark as paid when `payment_status` is `finished`). Instant notifications let you react in real-time without polling.

### List Payments

**Endpoint:** `GET /payment` (with query parameters)
Retrieves a list of payments associated with your account, optionally filtered by date, status, or currency. This is useful for building an overview of transactions or reconciling in your system.

**Available Query Parameters:** (all are optional)

* **limit** (int) – Maximum number of payments to return per page (default may be 10).
* **page** (int) – Page index for pagination (starting from 0 or 1, per API spec).
* **order\_by** (string) – Field to sort by (e.g. `created_at`, `payment_id`).
* **order** (string) – Sort direction: `asc` or `desc`.
* **dateFrom** (string) – Start date filter (ISO 8601 datetime or YYYY-MM-DD) – include payments created *after* this date.
* **dateTo** (string) – End date filter – include payments created *before* this date.
* **payment\_status** (string) – Filter by status (e.g. `waiting`, `finished`, etc.).
* **pay\_currency** (string) – Filter by the cryptocurrency used to pay (e.g. only payments made in BTC).

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/payment?limit=10&page=0&order_by=created_at&order=asc&dateFrom=2020-01-01&dateTo=2021-01-01" \
     -H "x-api-key: YOUR_API_KEY"
```

This would fetch the first 10 payments created in the year 2020, sorted by creation date ascending.

**Example Response:**

```json
{
  "data": [
    {
      "payment_id": 5524759814,
      "payment_status": "finished",
      "price_amount": 5,
      "price_currency": "usd",
      "pay_amount": 165.652609,
      "pay_currency": "trx",
      "pay_address": "TNDFkiSmBQorNFacb3735q8MnT29sn8BLn",
      "order_id": "RGDBP-21314",
      "order_description": "Apple Macbook Pro 2019 x 1",
      "purchase_id": "4944856743",
      "actually_paid": 180,
      "outcome_amount": 178.9005,
      "outcome_currency": "trx",
      "created_at": "2020-07-01T10:00:00.000Z",
      "updated_at": "2020-07-01T10:10:00.000Z"
    },
    ... (up to 10 payments)
  ],
  "limit": 10,
  "page": 0,
  "pagesCount": 6,
  "total": 59
}
```

The response provides an array of payment records under `data`. It also includes `total` (total number of payments matching the query), `pagesCount`, etc., for pagination.

### Update Payment Estimate

If a payment has not yet been paid and its exchange rate quote has expired, you may update the payment with a new rate (i.e., refresh the amount the customer needs to pay). This is relevant for payments where the customer delays payment past the original rate lock period.

**Endpoint:** `POST /payment/{payment_id}/update-merchant-estimate`

This endpoint recalculates the pay\_amount for an existing payment using current rates, if the previous estimate has expired. If the estimate is still valid (before expiration), the response will simply return the current payment data without changing the required amount.

* **Usage:** Only applicable while a payment is in `waiting` (unpaid) status and the original rate has expired or is about to expire.
* **Authentication:** API key required.
* **Request body:** *None.* (The payment ID in the URL is sufficient.)

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/payment/4409701815/update-merchant-estimate" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:** (if successful)

```json
{
  "payment_id": 4409701815,
  "payment_status": "waiting",
  "pay_amount": 0.00531234,
  "pay_currency": "btc",
  "price_amount": 100,
  "price_currency": "usd",
  "expire_at": "2025-08-07T16:45:00.000Z",
  ... (other fields as in payment status)
}
```

The `pay_amount` may be updated to a new value based on the latest exchange rate. The response structure is similar to Get Payment Status, reflecting the payment’s current data. If the estimate was updated, the `expire_at` might be extended. If called before the original estimate expired, it might return the same amount and not reset the timer.

### Create Invoice

NOWPayments can create hosted invoices – payment pages with unique URLs and QR codes – which your customers can use to pay without leaving your site workflow. Invoices are useful if you want to send a payment link via email or have a standalone payment page.

**Endpoint:** `POST /invoice`

This will generate a new invoice and return a URL that the customer can be redirected to in order to complete the payment.

**Parameters (JSON body):** The Create Invoice endpoint uses similar fields to Create Payment, except that it does not require specifying the pay\_currency upfront (the customer will choose the cryptocurrency on the invoice page). Required fields include:

* **price\_amount** – **Required.** Fiat price of the item or invoice amount.
* **price\_currency** – **Required.** Fiat currency for the amount (e.g. "usd", "eur").
* **order\_id** – **Required.** Your internal order or invoice identifier.
* **order\_description** – (Optional) Description of the invoice.
* **ipn\_callback\_url** – (Optional) IPN URL for status notifications (same as in Create Payment).
* **success\_url** – (Optional) URL to which the customer will be redirected after a successful payment.
* **cancel\_url** – (Optional) URL to which the customer will be redirected if they cancel the payment or the payment expires.

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/invoice" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "price_amount": 1000,
           "price_currency": "usd",
           "order_id": "INV-100500",
           "order_description": "Consulting Services Package",
           "ipn_callback_url": "https://example.com/ipn",
           "success_url": "https://example.com/thank-you",
           "cancel_url": "https://example.com/payment-cancelled"
         }'
```

**Example Response:**

```json
{
  "invoice_id": "X6JHJKJH2389",
  "invoice_url": "https://nowpayments.io/invoice?id=X6JHJKJH2389",
  "order_id": "INV-100500",
  "created_at": "2025-08-07T16:30:00.000Z",
  "price_amount": 1000,
  "price_currency": "usd",
  "pay_currency": null,
  "payment_id": null,
  "invoice_status": "waiting"
}
```

Key fields:

* `invoice_id` and `invoice_url` – the unique identifier and the URL where the customer can pay. You can redirect the customer to this URL or embed it as a link/QR code.
* Initially, `invoice_status` is `waiting` and no specific crypto `pay_currency` or `payment_id` is set until the customer initiates payment.
* Once the customer selects a crypto and pays via the invoice page, the invoice will internally create a payment (with a payment\_id). The `invoice_status` will update (e.g. to `finished` when paid), and the `payment_id` field may be populated with the underlying payment’s ID for reference.

You can query the invoice status via the next endpoint.

### Get Invoice Status

**Endpoint:** `GET /invoice/{invoice_id}`

Retrieves the current status and details of an invoice by its ID.

* **URL Parameter:** `invoice_id` – The ID of the invoice (as returned when creating it).
* **Authentication:** API key required.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/invoice/X6JHJKJH2389" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "invoice_id": "X6JHJKJH2389",
  "order_id": "INV-100500",
  "price_amount": 1000,
  "price_currency": "usd",
  "invoice_status": "finished",
  "pay_currency": "btc",
  "pay_amount": 0.0275,
  "payment_id": 5524890000,
  "created_at": "2025-08-07T16:30:00.000Z",
  "updated_at": "2025-08-07T16:45:10.000Z"
}
```

If the invoice was paid, `invoice_status` will be `"finished"` (or `"partially_paid"`, etc., depending on outcome), and the fields `pay_currency`, `pay_amount`, and `payment_id` will reflect the cryptocurrency and payment that was completed on that invoice. If the invoice is still awaiting payment, `invoice_status` remains `"waiting"` and those fields may be null.

*Note:* Invoices are a higher-level abstraction. Each invoice can result in one payment. To get detailed payment info, you can use the `payment_id` from this invoice with the Get Payment Status endpoint.

### Create Payment by Invoice

**Endpoint:** `POST /invoice-payment`

This endpoint creates a new payment tied to an existing invoice. It is used in scenarios where you want to programmatically initiate a payment for an invoice (for example, if the customer chooses a currency on your site and you want to get a payment address without redirecting). Essentially, it generates a payment for a previously created invoice ID, specifying the crypto and other details.

**Parameters (JSON body):**

* **iid** (string) – **Required.** The invoice ID for which to create a payment. This ties the new payment to that invoice.
* **pay\_currency** (string) – **Required.** The cryptocurrency the customer will pay in (e.g. `"btc"`).
* **purchase\_id** (string) – (Optional) A purchase/order identifier, similar to the field in Create Payment, if you want to group this payment.
* **order\_description** (string) – (Optional) Description of what is being paid for.
* **customer\_email** (string) – (Optional) The email of the customer to send the payment link to (if applicable).
* **payout\_address** (string) – (Optional) A specific outcome wallet address for this payment’s funds to go to (overrides default). Useful in certain flows (like a direct payout to a user).
* **payout\_extra\_id** (string) – (Optional) Extra ID or memo for the payout address (if the payout address requires a memo/tag, e.g. for XRP, XLM, etc.).
* **payout\_currency** (string) – (Optional) The currency in which you want to receive the payout for this invoice payment (if different from the pay\_currency).

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/invoice-payment" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "iid": "X6JHJKJH2389",
           "pay_currency": "btc",
           "purchase_id": "6084744717",
           "order_description": "Apple Macbook Pro 2019 x 1",
           "customer_email": "[email protected]",
           "payout_address": "0xYourWalletAddressHere",
           "payout_extra_id": null,
           "payout_currency": "usdttrc20"
         }'
```



In this example, we create a BTC payment for invoice `X6JHJKJH2389`. The funds, once paid, will be converted to USDT (Tron) and sent to the specified payout address. The customer’s email is provided, potentially to send them the invoice or confirmation.

**Example Response:**

```json
{
  "payment_id": 5524901234,
  "payment_status": "waiting",
  "pay_address": "bc1q....", 
  "pay_currency": "btc",
  "pay_amount": 0.0275,
  "invoice_id": "X6JHJKJH2389",
  "invoice_status": "waiting",
  "payout_currency": "usdttrc20",
  "payout_address": "0xYourWalletAddressHere",
  "created_at": "2025-08-07T16:40:00.000Z"
}
```

This indicates a payment was successfully created for the invoice. The customer should send `0.0275 BTC` to the provided address. Once paid and confirmed, the invoice\_status will update to finished and the funds will be delivered in USDT (Tron) to the given payout address.

## Recurring Payments API (Subscriptions)

The Recurring Payments API – also called the Email Subscriptions feature – allows you to charge customers on a regular schedule via email payment links. This is useful for subscription-based services (e.g. monthly memberships). It involves setting up a **plan** (defining the recurring charge details) and then creating **recurring payments** (subscriptions) for individual customers based on that plan.

### Create a Recurring Payment Plan

Before adding subscribers, you must create a subscription plan that defines the billing cycle and amount.

**Endpoint:** `POST /subscriptions/plans`

**Parameters (JSON body):**

* **title** (string) – **Required.** A name for the recurring payments plan (e.g. `"Premium Monthly Subscription"`).
* **interval\_day** (integer) – **Required.** The interval between payments in days. For example, `30` for monthly, `7` for weekly, etc.
* **amount** (decimal) – **Required.** The amount to charge each period, in fiat currency. (This is the fiat value per cycle.)
* **currency** (string) – **Required.** The fiat currency of the amount (e.g. `"usd"` for US Dollars).
* **ipn\_callback\_url** (string) – (Optional) IPN callback URL for this subscription plan’s payments (overrides global IPN if set).
* **success\_url** (string) – (Optional) URL to redirect a customer to after a successful recurring payment.
* **cancel\_url** (string) – (Optional) URL to redirect if a payment in the plan is canceled or fails.
* **partially\_paid\_url** (string) – (Optional) URL to redirect if a recurring payment was made but not fully paid (partial payment scenario).

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/subscriptions/plans" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "My Premium Plan",
           "interval_day": 30,
           "amount": 50,
           "currency": "usd",
           "ipn_callback_url": "https://example.com/sub-ipn",
           "success_url": "https://example.com/sub-success",
           "cancel_url": "https://example.com/sub-cancel",
           "partially_paid_url": "https://example.com/sub-partial"
         }'
```



**Example Response:**

```json
{
  "result": {
    "id": "123456789",
    "title": "My Premium Plan",
    "interval_day": "30",
    "amount": 50,
    "currency": "USD",
    "ipn_callback_url": null,
    "success_url": null,
    "cancel_url": null,
    "partially_paid_url": null,
    "created_at": "2022-10-04T16:28:55.423Z",
    "updated_at": "2022-10-04T16:28:55.423Z"
  }
}
```



The response includes the newly created plan’s details, especially the **`id`** which is the plan’s unique identifier. You will need this plan ID to create individual subscriptions.

### Update a Recurring Payment Plan

If you need to change the parameters of an existing plan (e.g. price or interval), you can update it. Changes will not affect already-paid upcoming charges for subscribers, but will apply to future billing cycles.

**Endpoint:** `PATCH /subscriptions/plans/{plan_id}`

* **URL Parameter:** `plan_id` – The ID of the plan to update.
* **Body:** Include only the fields you want to update (same fields as in plan creation). For example, you might send `{"amount": 60}` to change the fiat amount for future cycles to \$60.

**Example Request:**

```shell
curl -X PATCH "https://api.nowpayments.io/v1/subscriptions/plans/123456789" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{ "amount": 60 }'
```

**Response:** Returns the updated plan object (similar format to creation response) with new values.

*(Note: Updating a plan does not retroactively change amounts for already invoiced periods or subscriptions currently mid-cycle; it only affects new cycles going forward.)*

### Get Subscription Plan Details

You can retrieve information on a single plan or all your plans.

* **Endpoint (one plan):** `GET /subscriptions/plans/{plan_id}` – returns details of the specified plan.
* **Endpoint (all plans):** `GET /subscriptions/plans` – returns an array of all plans you have created.

**Example Request (single plan):**

```shell
curl -X GET "https://api.nowpayments.io/v1/subscriptions/plans/123456789" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "id": "123456789",
  "title": "My Premium Plan",
  "interval_day": "30",
  "amount": 50,
  "currency": "USD",
  "created_at": "2022-10-04T16:28:55.423Z",
  "updated_at": "2022-10-04T16:28:55.423Z"
}
```

For getting all plans:

```shell
curl -X GET "https://api.nowpayments.io/v1/subscriptions/plans" \
     -H "x-api-key: YOUR_API_KEY"
```

This will return a list of plan objects.

### Create an Email Subscription (Recurring Payment)

Once a plan is in place, you can subscribe a customer to it. Creating a subscription will automatically email the customer a payment link for the initial payment, and send new payment links before each subsequent billing cycle.

**Endpoint:** `POST /subscriptions`

**Parameters (JSON body):**

* **plan\_id** (string) – **Required.** The ID of the recurring plan the customer is subscribing to.
* **email** (string) – **Required.** The customer’s email address where payment links will be sent.
* **order\_id** (string) – (Optional) An internal identifier for this subscriber or subscription.
* **order\_description** (string) – (Optional) Description for this subscription (e.g. what service or product it is for).
* **customer\_name** (string) – (Optional) Name of the customer (could be used in email communication).
* **starting\_day** (integer) – (Optional) If you want to schedule the first payment to start later, you can specify in how many days the first charge should occur (otherwise, it starts immediately or on the next cycle as per plan).

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/subscriptions" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "plan_id": "123456789",
           "email": "[email protected]",
           "order_id": "SUB-0001",
           "order_description": "Premium Plan Subscription",
           "customer_name": "John Doe"
         }'
```

Upon calling this, NOWPayments will immediately (or on the scheduled start) send an email to the provided address containing a payment link for the subscription. The customer will need to pay that link to start the subscription. A day before each new period, a new payment link email will be sent automatically.

**Example Response:**

```json
{
  "subscription_id": "987654321",
  "plan_id": "123456789",
  "email": "[email protected]",
  "order_id": "SUB-0001",
  "order_description": "Premium Plan Subscription",
  "status": "waiting",
  "next_payment_date": "2025-09-07T00:00:00Z",
  "created_at": "2025-08-07T16:50:00.000Z"
}
```

* `subscription_id` is the unique ID of this recurring subscription.
* `status` indicates the state of the subscription’s latest payment (`waiting` means the initial payment link is awaiting payment). This status will update to `finished` once the customer pays, and cycle back to `waiting` for each new invoice period.
* `next_payment_date` indicates when the next charge is scheduled (if the current one is paid).

### List Recurring Payments (Subscriptions)

**Endpoint:** `GET /subscriptions` (with optional filters)

Retrieves all recurring payment subscriptions under your account, with optional filtering by status or plan.

**Query Parameters:**

* **plan\_id** (string) – Filter subscriptions by a specific plan ID.
* **status** (string) – Filter by subscription status (e.g. `active`, `waiting`, `finished`, etc. – status naming here might reflect overall subscription state or last payment state).
* **limit, page** – Pagination controls similar to List Payments.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/subscriptions?plan_id=123456789&status=active" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "data": [
    {
      "subscription_id": "987654321",
      "plan_id": "123456789",
      "email": "[email protected]",
      "order_id": "SUB-0001",
      "status": "active",
      "created_at": "2025-08-07T16:50:00.000Z",
      "last_payment_date": "2025-08-07T17:00:00.000Z",
      "next_payment_date": "2025-09-07T00:00:00Z"
    },
    ...
  ],
  "total": 1,
  "page": 0,
  "limit": 50,
  "pagesCount": 1
}
```

This shows an “active” subscription for the plan. An active status likely means the latest payment was completed and future ones are scheduled. If a payment is missed or pending, status might reflect that (e.g. `waiting`).

### Get Subscription (Recurring Payment) Details

**Endpoint:** `GET /subscriptions/{subscription_id}`

Gets detailed information about a specific recurring subscription (including its current status and associated plan).

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/subscriptions/987654321" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "subscription_id": "987654321",
  "plan_id": "123456789",
  "email": "[email protected]",
  "order_id": "SUB-0001",
  "order_description": "Premium Plan Subscription",
  "status": "active",
  "created_at": "2025-08-07T16:50:00.000Z",
  "last_payment": {
    "payment_id": 5525000000,
    "status": "finished",
    "paid_amount_crypto": "0.001234 BTC",
    "paid_date": "2025-08-07T17:00:00.000Z"
  },
  "next_payment_due": "2025-09-07T00:00:00Z"
}
```

This includes the subscription’s metadata and possibly an embedded summary of the last payment made (`last_payment`) and when the next payment is due.

### Cancel (Delete) a Recurring Subscription

If a customer cancels their subscription or you need to stop it, you can delete the recurring payment entry.

**Endpoint:** `DELETE /subscriptions/{subscription_id}`

This will cancel the subscription so that no further payment links are sent. (If a payment link was already sent and pending, that payment will effectively be invalidated or ignored after cancellation.)

**Example Request:**

```shell
curl -X DELETE "https://api.nowpayments.io/v1/subscriptions/987654321" \
     -H "x-api-key: YOUR_API_KEY"
```

**Response:** On success, returns a confirmation (e.g. HTTP 204 No Content or a JSON message indicating deletion success).

**Note:** In the request to delete, you may need to supply the plan ID or other authentication to ensure you intend to cancel the correct subscription. The NOWPayments documentation suggests specifying the plan ID in the request for deletion as well, though the exact method may vary (it could be a query parameter or part of the request body). Ensure you follow the official docs for the correct deletion procedure.

After deletion, the subscription’s status will change (e.g. to "cancelled"), and no new invoices will be generated for that subscription.

## Payouts API (Mass Payouts)

The Payouts API allows partners to send cryptocurrency payments *outgoing* to multiple wallet addresses in a batch, with just one API call. This is useful for payroll, affiliate payouts, refunds, or any scenario where you need to pay many recipients at once. NOWPayments’ Mass Payouts feature bundles multiple transfers into one batch to save on fees.

**Important Security:** The Payouts API is a high-security feature. You must have **Custody enabled** (since payouts draw from your stored balance) and use **whitelisted IPs** and **2FA verification** to initiate payouts. Each payout creation must be verified with a 2FA code (Time-based OTP) unless you have explicitly disabled 2FA (not recommended).

### Create a Payout (Batch Withdrawal)

Creates a new payout batch to send funds to one or multiple recipients. Each batch can contain one or many withdrawal entries.

**Endpoint:** `POST /payout`

**Headers:**

* `x-api-key: YOUR_API_KEY`
* `Authorization: Bearer YOUR_JWT_TOKEN` – A JWT token obtained by verifying your 2FA code (or directly a token generated from your 2FA secret). In practice, you must either include a valid 2FA token here or verify the payout in the next step with a code. The NOWPayments documentation indicates that the `Authorization: Bearer` header is used for 2FA token.

**Request Body Fields:**

* **withdrawals** (array of objects) – **Required.** A list of withdrawal instructions in this batch. Each object in the array should include:

  * **address** (string) – The recipient’s wallet address to send funds to.
  * **currency** (string) – The cryptocurrency ticker of the asset to send (e.g. `"btc"`, `"eth"`, `"trx"`). Each withdrawal can potentially be a different currency, or all the same – depending on your needs.
  * **amount** (decimal) – The amount of the specified cryptocurrency to send.
  * **ipn\_callback\_url** (string) – (Optional, per withdrawal) An IPN URL to receive a callback when *that specific payout* status changes (sent, completed, etc.). You can set this per withdrawal or rely on a global IPN for all payouts.
  * **fiat\_amount** (decimal) – *(Optional)* If you prefer to specify the payout in fiat terms and let NOWPayments convert to crypto, you can provide a fiat amount instead of a crypto amount. If `fiat_amount` is provided, you should also provide **fiat\_currency**.
  * **fiat\_currency** (string) – *(Optional)* The fiat currency code (e.g. `"usd"`) corresponding to fiat\_amount. NOWPayments will convert this fiat amount to the appropriate crypto amount for the payout at the time of processing.

* **ipn\_callback\_url** (string) – (Optional, batch-level) You can also specify a general IPN callback for the entire batch. If provided, NOWPayments will send payout status updates for the batch to this URL.

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/payout" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_2FA_JWT" \
     -d '{
           "ipn_callback_url": "https://example.com/payout-callback",
           "withdrawals": [
             {
               "address": "TEmGwPeRTPiLFLVfBxXkSP91yc5GMNQhfS",
               "currency": "trx",
               "amount": 200,
               "ipn_callback_url": "https://example.com/payout-single-callback"
             },
             {
               "address": "0x1EBAeF7Bee7B3a7B2EEfC72e86593Bf15ED37522",
               "currency": "eth",
               "amount": 0.1,
               "ipn_callback_url": "https://example.com/payout-single-callback"
             },
             {
               "address": "0x1EBAeF7Bee7B3a7B2EEfC72e86593Bf15ED37522",
               "currency": "usdc",
               "amount": 1,
               "fiat_amount": 100,
               "fiat_currency": "usd",
               "ipn_callback_url": "https://example.com/payout-single-callback"
             }
           ]
         }'
```



In this example, we create a batch with three payouts: 200 TRX to a TRON address, 0.1 ETH to an Ethereum address, and the equivalent of \$100 in USDC to an Ethereum address. Each has its own callback, and we also set a general callback for the batch.

**Example Response:** (on successful creation)

```json
{
  "batch_id": "Batch123456",
  "status": "created",
  "total_amount": 1.1,
  "total_currency": "ETH", 
  "created_at": "2025-08-07T17:00:00.000Z",
  "withdrawals": [
    {
      "id": "wd1",
      "address": "TEmGwPeRTPiLFLVfBxXkSP91yc5GMNQhfS",
      "currency": "trx",
      "amount": 200,
      "status": "pending"
    },
    {
      "id": "wd2",
      "address": "0x1EBAeF7Bee7B3a7B2EEfC72e86593Bf15ED37522",
      "currency": "eth",
      "amount": 0.1,
      "status": "pending"
    },
    {
      "id": "wd3",
      "address": "0x1EBAeF7Bee7B3a7B2EEfC72e86593Bf15ED37522",
      "currency": "usdc",
      "amount": 100,
      "amount_fiat": 100,
      "fiat_currency": "usd",
      "status": "pending"
    }
  ]
}
```

* `batch_id` is the unique identifier for this payout batch.
* `status` initially is `"created"` (or `"waiting_verification"` if 2FA not yet verified).
* Each withdrawal has its own `id` and status (`pending` meaning not yet sent).
* The response might also include a `total_amount` and `total_currency` if applicable (e.g. summarizing totals per currency or converted to a single currency).
* **Note:** At this stage, if the batch requires 2FA verification, it may not execute until verified.

### Verify Payout (2FA Confirmation)

After creating a payout, you must verify it with your 2FA code to authorize the transfers. This step is required if you haven’t already provided a valid authorization token.

**Endpoint:** `POST /payout/{batch_id}/verify`

**Parameters:** You need to supply the 2FA one-time password code (the 6-digit code from your authenticator or the code sent to your email, depending on your 2FA method) in the request. The code might be provided in the JSON body, for example: `{ "code": "123456" }`.

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/payout/Batch123456/verify" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{ "code": "123456" }'
```

This assumes `"Batch123456"` is the batch\_id that was returned when creating the payout, and "123456" is the current 2FA code.

**Response:** On success, the payout status will transition to "sending" or "sent" and the transfers will be broadcast. The API may return an updated batch status object:

```json
{
  "batch_id": "Batch123456",
  "status": "sending",
  "verified_at": "2025-08-07T17:02:00.000Z"
}
```

If the code is incorrect, you'll get an error. The API allows a limited number of attempts (10 attempts) to verify with the correct code before the payout is locked or canceled.

### Get Payout Status

You can query the status of a payout batch to see if it’s completed, pending, or failed.

**Endpoint:** `GET /payout/{batch_id}`

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/payout/Batch123456" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "batch_id": "Batch123456",
  "status": "finished",
  "created_at": "2025-08-07T17:00:00.000Z",
  "updated_at": "2025-08-07T17:05:30.000Z",
  "withdrawals": [
    {
      "id": "wd1",
      "currency": "trx",
      "amount": 200,
      "status": "finished",
      "txid": "abcd1234...ef", 
      "finished_at": "2025-08-07T17:03:10.000Z"
    },
    {
      "id": "wd2",
      "currency": "eth",
      "amount": 0.1,
      "status": "finished",
      "txid": "0xabcdef...123456",
      "finished_at": "2025-08-07T17:04:00.000Z"
    },
    {
      "id": "wd3",
      "currency": "usdc",
      "amount": 100,
      "fiat_currency": "usd",
      "status": "finished",
      "txid": "0x987654...321abc",
      "finished_at": "2025-08-07T17:04:30.000Z"
    }
  ]
}
```

Here `status: "finished"` indicates the batch has been fully processed. Each withdrawal entry shows a status (e.g. finished, or could be failed if one transfer failed) and possibly a transaction ID (`txid`) for blockchain reference. If any withdrawal fails (invalid address, etc.), its status would be `"failed"` and the batch status might be `"finished_with_errors"` or similar.

### List Payouts

**Endpoint:** `GET /payout` (with filters)

Retrieves a list of payout batches, optionally filtered by status, date, etc.

**Query Parameters:**

* **batch\_id** (string) – Filter by a specific batch ID (to find a particular batch easily).
* **status** (string) – Filter by batch status (`created`, `sending`, `finished`, etc.).
* **date\_from, date\_to** – Filter by creation date range.
* **order\_by, order** – Sort options (e.g. order\_by `id` or `created_at`, ascending/descending).
* **limit, page** – Pagination parameters.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/payout?status=sending&limit=20&page=0" \
     -H "x-api-key: YOUR_API_KEY"
```

This would list your payout batches that are currently in "sending" status, 20 per page.

**Example Response:**

```json
{
  "data": [
    {
      "batch_id": "Batch123456",
      "status": "finished",
      "total_amount": 1.1,
      "total_currency": "ETH",
      "created_at": "2025-08-07T17:00:00.000Z",
      "updated_at": "2025-08-07T17:05:30.000Z"
    },
    {
      "batch_id": "Batch987654",
      "status": "failed",
      "total_amount": 0.5,
      "total_currency": "BTC",
      "created_at": "2025-08-01T12:00:00.000Z",
      "updated_at": "2025-08-01T12:05:00.000Z"
    },
    ...
  ],
  "limit": 20,
  "page": 0,
  "total": 5,
  "pagesCount": 1
}
```

This shows a list of payout batches with their high-level status. (Detailed withdrawals are not listed here; they are retrieved via the individual batch endpoint.)

### Validate Payout Address

Before creating a payout, you can optionally validate that a payout address is valid for the intended currency. This can help reduce errors due to typos or unsupported address formats.

**Endpoint:** `POST /payout/validate-address`

**Parameters (JSON body):**

* **address** (string) – **Required.** The cryptocurrency address to validate.
* **currency** (string) – **Required.** The cryptocurrency ticker symbol that the address is supposed to correspond to (e.g. `"btc"`, `"eth"`, `"xlm"`).
* **extra\_id** (string) – (Optional) If the currency requires an extra identifier (memo, destination tag, etc.), provide it here for validation as well. (E.g. for XRP, an address might require a destination tag; for XLM, a memo.)

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/payout/validate-address" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "address": "0x1EBAeF7Bee7B3a7B2EEfC72e86593Bf15ED37522",
           "currency": "eth"
         }'
```



**Example Response:**

```json
{
  "address": "0x1EBAeF7Bee7B3a7B2EEfC72e86593Bf15ED37522",
  "currency": "eth",
  "result": true,
  "message": "Address is valid."
}
```

If the address was invalid, `result` would be `false` and `message` would contain an error (for example, "Invalid address format" or details about why it’s not valid). This endpoint helps prevent attempting payouts to malformed addresses.

## Custody (Extended API for Sub-Accounts)

NOWPayments offers a Custody API (sometimes referred to as the “Extended Custody” or “Sub-Partner” API). This allows partners (merchants) to create and manage **user accounts** under their master account. Each sub-account can have its own balance, deposits, and withdrawals, enabling use-cases like: managing user deposits, internal transfers, and aggregating funds for later payout. This is especially useful for platforms like exchanges, casinos, marketplaces, etc., where you want to give users individual deposit addresses and track their balances using NOWPayments infrastructure.

Key features of the Custody API include:

* Creating user accounts (sub-accounts) under your master account.
* Generating deposit addresses for users to top-up their balance.
* Transferring funds between the master account and sub-accounts, or between sub-accounts.
* Checking balances of sub-accounts.
* Withdrawing funds from sub-accounts to the master (or directly to external wallets, depending on method).
* Managing multiple users and handling mass deposits/payouts internally.

**Security:** Custody API calls require IP whitelisting as well. Ensure your server’s IP is whitelisted for Custody operations. 2FA might also apply to certain write operations (like withdrawals from custody).

All Custody endpoints are under the base path `/sub-partner`.

### Create a New User Account

This creates a new sub-account (user account) under your master account. When a user account is created, you can start generating deposit addresses for it and track its balance.

**Endpoint:** `POST /sub-partner/balance`

**Parameters (JSON body):** You may include optional info such as:

* **user\_id** or **external\_id** (string) – (Optional) An identifier for the user in your system. If provided, this could be stored or echoed by the API (for your reference).
* **email** (string) – (Optional) If you want to tie an email to the sub-account.

*(The official documentation doesn't list required fields besides the API key; posting to this endpoint is enough to create a user account.)*

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/sub-partner/balance" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{ "external_id": "user_12345", "email": "[email protected]" }'
```



**Example Response:**

```json
{
  "user_id": 111,
  "external_id": "user_12345",
  "balance": [],
  "created_at": "2025-08-07T18:00:00.000Z"
}
```

* `user_id` is the internal ID of the created sub-account (assigned by NOWPayments). This is used for other API calls to reference the user.
* `balance` may be an array of balance objects per currency (empty if no funds yet).
* The response might also echo back the provided external\_id or email if given.

Now you have a sub-account that can receive deposits.

### Get User Balance

Fetches the balances of a specific user account (sub-partner) across all currencies.

**Endpoint:** `GET /sub-partner/balance/{user_id}`

**Requirements:** This request **must** come from a whitelisted IP address (for security).

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/sub-partner/balance/111" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "user_id": 111,
  "balance": [
    { "currency": "btc", "amount": 0.0025 },
    { "currency": "eth", "amount": 1.5 },
    { "currency": "usd", "amount": 100.0 }
  ]
}
```

This shows user 111 has 0.0025 BTC, 1.5 ETH, and \$100 (USD) in their custody balance. Fiat balances (like USD) mean the user has that amount in stable form (likely from conversions). The API only returns balances that have been transited through NOWPayments (a new user starts with no balances).

### List User Accounts

**Endpoint:** `GET /sub-partner`

Retrieves a list of all your sub-accounts (users).

**Query Parameters:**

* **offset** and **limit** for pagination (e.g. `?offset=0&limit=10`).
* **order** (ASC or DESC) and **order\_by** (perhaps by `id` or creation date) to sort.
* **id** (if provided, possibly filters by a specific user id – though normally you’d use /balance/{id} for single user).

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/sub-partner?limit=10&offset=0&order=DESC" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "users": [
    { "user_id": 111, "external_id": "user_12345", "created_at": "2025-08-07T18:00:00.000Z" },
    { "user_id": 112, "external_id": "user_67890", "created_at": "2025-08-07T18:05:00.000Z" },
    ...
  ],
  "limit": 10,
  "offset": 0,
  "total": 2
}
```

This lists your sub-partner accounts with basic info. The `total` indicates how many sub-accounts exist.

### Generate a Payment (Deposit) for User

This endpoint generates a deposit address or payment link for a sub-account to top up their balance in a specific cryptocurrency. Essentially, it’s similar to creating a payment, but the funds will credit the user’s custody balance rather than immediately being settled to your master wallet.

**Endpoint:** `POST /sub-partner/payment`

**Parameters (JSON body):**

* **user\_id** (integer) – **Required.** The sub-account’s user ID that should receive the deposit.
* **currency** (string) – **Required.** The cryptocurrency the user will deposit.
* **amount** (decimal) – (Optional) The exact amount in crypto expected. If you know how much the user will deposit, you can specify it; otherwise, you might leave it open.
* **track\_id** (string) – (Optional) An external tracking ID for this deposit request (for your own reconciliation).
* **pay\_currency** (alias for currency)\*\* – depending on API version, the field might also be called pay\_currency; conceptually it’s the coin being paid.

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/sub-partner/payment" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": 111,
           "currency": "btc",
           "amount": 0.01,
           "track_id": "deposit_001"
         }'
```

**Example Response:**

```json
{
  "payment_id": 6677889900,
  "user_id": 111,
  "pay_address": "bc1qw4...xyz",
  "currency": "btc",
  "amount": 0.01,
  "status": "waiting",
  "created_at": "2025-08-07T18:10:00.000Z",
  "track_id": "deposit_001"
}
```

This provides a Bitcoin deposit address (`pay_address`) where the user should send 0.01 BTC. Once the user sends the BTC and it gets confirmed, NOWPayments will credit user 111’s balance by that amount. The status will update to "finished" when the deposit is complete.

If you don’t specify an amount, `pay_address` can still be used and the user’s entire deposit to that address will be credited.

### Transfers Between Accounts

The Custody API supports transferring funds internally:

* Between two sub-accounts, or
* Between a sub-account and the master account.

**Endpoint:** `POST /sub-partner/transfer`

**Parameters:**

* **from\_id** (integer) – **Required.** The user ID to transfer funds from. Use a special identifier or your master account ID if transferring from master. (Often, master might be represented as `0` or some specific flag in the API; documentation should clarify.)
* **to\_id** (integer) – **Required.** The user ID to transfer funds to. Use master account ID or `0` if transferring to master from a user.
* **currency** (string) – **Required.** The currency to transfer. The currency must be available in the source account’s balance.
* **amount** (decimal) – **Required.** The amount to transfer.

**Example (User-to-User) Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/sub-partner/transfer" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "from_id": 111,
           "to_id": 112,
           "currency": "usd",
           "amount": 25
         }'
```

This would transfer \$25 from user 111’s balance to user 112’s balance (assuming both have USD balance in custody).

**Example Response:**

```json
{
  "transfer_id": "TR-555",
  "from_id": 111,
  "to_id": 112,
  "currency": "USD",
  "amount": 25,
  "status": "completed",
  "created_at": "2025-08-07T18:30:00.000Z"
}
```

Now user 111’s USD balance would decrease by 25, and user 112’s increases by 25.

**Transfers to/from Master:** To move funds out of a user account back to your main account (for example, when a user makes a withdrawal request on your platform), you would call transfer with `to_id` as the master. If the API uses `id` query as shown in blog for listing transfers, it suggests filtering by user. But typically:

* **Withdraw from user (to master):** `from_id = user_id`, `to_id = master_id (or 0)`.
* **Deposit to user (from master):** `from_id = master`, `to_id = user_id`.

*(The exact representation of master in the API might simply be omitting user or using your partner account ID. In absence of explicit docs, one common approach is using `0` or an empty from/to to signify master. Check NOWPayments documentation for the proper usage.)*

### List Transfers

**Endpoint:** `GET /sub-partner/transfers`

Lists transfer records between accounts.

**Query Params:**

* **id** – filter by a specific user ID (e.g. `?id=111` to get transfers involving user 111).
* **status** – filter by transfer status (`CREATED`, `COMPLETED`, etc.).
* **limit, offset, order** – pagination and sorting.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/sub-partner/transfers?status=COMPLETED&limit=10" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "transfers": [
    {
      "transfer_id": "TR-555",
      "from_id": 111,
      "to_id": 112,
      "currency": "USD",
      "amount": 25,
      "status": "completed",
      "created_at": "2025-08-07T18:30:00.000Z"
    },
    {
      "transfer_id": "TR-556",
      "from_id": 111,
      "to_id": 0,
      "currency": "ETH",
      "amount": 0.5,
      "status": "completed",
      "created_at": "2025-08-07T19:00:00.000Z"
    }
  ],
  "limit": 10,
  "offset": 0,
  "total": 2
}
```

This shows a transfer from user 111 to 112 (USD 25) and another from user 111 to master (0.5 ETH). `to_id: 0` could indicate master account in this context (assuming 0 is used for master).

### Get Transfer Details

**Endpoint:** `GET /sub-partner/transfer/{transfer_id}`

Retrieve details of a specific transfer by its ID.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/sub-partner/transfer/TR-555" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "transfer_id": "TR-555",
  "from_id": 111,
  "to_id": 112,
  "currency": "USD",
  "amount": 25,
  "status": "completed",
  "created_at": "2025-08-07T18:30:00.000Z",
  "completed_at": "2025-08-07T18:30:01.500Z"
}
```

For pending transfers, `status` might be `created` or `pending` until done.

### Withdraw Funds from a User (Write-off)

Withdraw (write-off) moves funds from a user’s balance back to your master account *and optionally triggers an external payout*. In other words, it’s how you take a user’s custody funds and send them out, either to your own master balance or directly out to an external address.

**Endpoint:** `POST /sub-partner/write-off`

**Parameters:**

* **user\_id** (integer) – **Required.** The user ID to withdraw from.
* **currency** (string) – **Required.** Currency to withdraw.
* **amount** (decimal) – **Required.** Amount to withdraw from the user’s balance.
* **address** (string) – (Optional) An external address to send the funds to. If provided, the funds will be sent out to this address. If not provided, the funds likely move to master account balance.
* **address\_extra** (string) – (Optional) Extra address info (memo/tag) if needed.
* **ipn\_callback\_url** (string) – (Optional) IPN for this withdrawal’s status.

**Example Request (withdraw to master):**

```shell
curl -X POST "https://api.nowpayments.io/v1/sub-partner/write-off" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": 111,
           "currency": "eth",
           "amount": 0.5
         }'
```

This would remove 0.5 ETH from user 111’s custody and credit it to your main account balance.

**Example Request (withdraw to external address):**

```shell
curl -X POST "https://api.nowpayments.io/v1/sub-partner/write-off" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": 112,
           "currency": "usdttrc20",
           "amount": 100,
           "address": "TLg8...someTronAddress",
           "ipn_callback_url": "https://example.com/withdraw-callback"
         }'
```

This attempts to send 100 USDT (Tron) from user 112’s balance to the specified TRON address. Essentially, it combines a transfer from user to master with an outgoing payout from master to an address, all in one call.

**Example Response:**

```json
{
  "withdrawal_id": "WD-1001",
  "user_id": 112,
  "currency": "USDTTRC20",
  "amount": 100,
  "address": "TLg8...someTronAddress",
  "status": "sending",
  "created_at": "2025-08-07T19:30:00.000Z"
}
```

You would then verify via IPN or query when `status` becomes `finished` and perhaps get a transaction hash.

**Note:** If 2FA is enabled, withdrawing to an external address might require a verification similar to the Payout verification (unless you have a JWT auth token already in headers). Ensure your IP is whitelisted and be prepared to supply a 2FA code if needed.

## Conversions API

The Conversions API allows you to convert funds from one cryptocurrency to another within your NOWPayments account (particularly within your Custody account). This can be useful to manage the assets you hold – for example, converting incoming payments to a stablecoin or consolidating various coins into one.

**Important:** Conversion happens within your account balances – no external addresses are involved. You must have a sufficient balance of the source currency in your custody for the conversion to proceed.

### Create Conversion

**Endpoint:** `POST /conversion`

**Parameters (JSON body):**

* **from\_currency** (string) – **Required.** The currency code you want to convert from (the asset you have).
* **to\_currency** (string) – **Required.** The currency code you want to convert to (the asset you want to receive).
* **amount** (decimal) – **Required.** The amount of `from_currency` to convert. This amount will be deducted from your balance of `from_currency`. The appropriate amount of `to_currency` will be added to your balance (based on current rates minus any fees).

**Example Request:**

```shell
curl -X POST "https://api.nowpayments.io/v1/conversion" \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "from_currency": "btc",
           "to_currency": "eth",
           "amount": 0.05
         }'
```

This would convert 0.05 BTC to Ethereum within your account (assuming you have at least 0.05 BTC in custody).

**Example Response:**

```json
{
  "conversion_id": "CV-0001",
  "from_currency": "BTC",
  "to_currency": "ETH",
  "from_amount": 0.05,
  "to_amount": 0.82,
  "status": "completed",
  "created_at": "2025-08-07T20:00:00.000Z",
  "rate": 16.4
}
```

Here, `to_amount: 0.82` ETH is the result of converting 0.05 BTC. The `rate` field shows the rate applied (in this case 1 BTC = 16.4 ETH equivalent). The status is `completed` indicating the conversion is done (it might be near-instant). If the status were `pending`, it might indicate it’s in process (though conversions are usually quick since they use an internal exchange service).

### Get Conversion Status

**Endpoint:** `GET /conversion/{conversion_id}`

Checks the status and result of a specific conversion by ID.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/conversion/CV-0001" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "conversion_id": "CV-0001",
  "from_currency": "BTC",
  "to_currency": "ETH",
  "from_amount": 0.05,
  "to_amount": 0.82,
  "status": "completed",
  "created_at": "2025-08-07T20:00:00.000Z",
  "completed_at": "2025-08-07T20:00:05.000Z",
  "rate": 16.4
}
```

If a conversion failed for some reason (perhaps liquidity issues), status might be `failed` and no funds would move.

### List Conversions

**Endpoint:** `GET /conversion`

Lists recent conversion transactions.

**Query parameters** could include filtering by status or currency, and pagination.

**Example Request:**

```shell
curl -X GET "https://api.nowpayments.io/v1/conversion?limit=10" \
     -H "x-api-key: YOUR_API_KEY"
```

**Example Response:**

```json
{
  "conversions": [
    {
      "conversion_id": "CV-0001",
      "from_currency": "BTC",
      "to_currency": "ETH",
      "from_amount": 0.05,
      "to_amount": 0.82,
      "status": "completed",
      "created_at": "2025-08-07T20:00:00.000Z"
    },
    {
      "conversion_id": "CV-0002",
      "from_currency": "BTC",
      "to_currency": "USDT",
      "from_amount": 0.01,
      "to_amount": 300,
      "status": "completed",
      "created_at": "2025-08-06T15:00:00.000Z"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

This shows two conversions that were done.

## Conclusion

This reference covered all publicly documented endpoints of the NOWPayments API, including Authentication, Payments (and Invoices), Recurring Payments (Subscriptions), Mass Payouts, Custody (sub-accounts), and Conversions. Each endpoint is described with its purpose, required and optional parameters, example cURL requests, and example responses for clarity. Use this as a guide for integrating NOWPayments into your application, and refer to the cited documentation for further details or any updates.

By following this reference, developers can build robust integrations with NOWPayments – from accepting crypto payments and subscriptions to managing user balances and automating payouts – all while handling necessary security requirements like API keys, IP whitelisting, and 2FA verification as documented.
