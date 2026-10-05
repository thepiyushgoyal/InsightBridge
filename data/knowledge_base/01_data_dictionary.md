# InsightBridge E-commerce Analytics Data Dictionary

This knowledge base describes a fictional e-commerce analytics warehouse used by the InsightBridge analytics team. All tables are assumed to live in the `analytics` schema.

## customers

Customer profile table. One row should represent one real customer account.

| Column | Type | Description |
| --- | --- | --- |
| customer_id | STRING | Primary key for a customer account. |
| email | STRING | Customer email address. May be duplicated before identity cleanup. |
| first_order_date | DATE | Date of the customer's first completed order. |
| signup_date | DATE | Date the customer created an account. |
| country | STRING | Customer billing country. |
| acquisition_channel | STRING | First-touch marketing channel, such as paid_search, organic, email, or referral. |
| is_duplicate | BOOLEAN | True when the customer account is flagged as a duplicate identity. |

Primary key: `customer_id`

Data-quality note: most customer-level analysis should exclude rows where `is_duplicate = TRUE` unless the analysis is specifically about duplicate identity cleanup.

## orders

Order header table. One row represents one checkout attempt that reached order creation.

| Column | Type | Description |
| --- | --- | --- |
| order_id | STRING | Primary key for an order. |
| customer_id | STRING | Foreign key to `customers.customer_id`. |
| order_date | DATE | Date the order was placed. |
| order_status | STRING | Order lifecycle status: completed, cancelled, returned, or pending. |
| gross_order_amount | DECIMAL | Order amount before refunds and payment adjustments. |
| currency | STRING | ISO currency code. The sample warehouse uses USD for executive reporting. |
| promo_code | STRING | Promotion code used at checkout, if any. |

Primary key: `order_id`

Foreign key: `customer_id` joins to `customers.customer_id`

Business note: revenue metrics exclude `order_status = 'cancelled'`.

## order_items

Line-item table. One row represents one product on an order.

| Column | Type | Description |
| --- | --- | --- |
| order_item_id | STRING | Primary key for an order line. |
| order_id | STRING | Foreign key to `orders.order_id`. |
| product_id | STRING | Foreign key to `products.product_id`. |
| quantity | INTEGER | Number of units purchased. |
| unit_price | DECIMAL | Unit price charged before tax. |
| item_discount | DECIMAL | Discount applied to this line item. |

Primary key: `order_item_id`

Foreign keys: `order_id` joins to `orders.order_id`; `product_id` joins to `products.product_id`

Line revenue formula: `(quantity * unit_price) - item_discount`

## products

Product dimension table.

| Column | Type | Description |
| --- | --- | --- |
| product_id | STRING | Primary key for a product. |
| product_name | STRING | Display name of the product. |
| category | STRING | Reporting category such as Apparel, Home, Beauty, Electronics, or Accessories. |
| brand | STRING | Product brand. |
| list_price | DECIMAL | Current list price. |
| active_flag | BOOLEAN | True when the product is currently active in the catalog. |

Primary key: `product_id`

## payments

Payment transaction table. One order can have one or more payment attempts.

| Column | Type | Description |
| --- | --- | --- |
| payment_id | STRING | Primary key for a payment transaction. |
| order_id | STRING | Foreign key to `orders.order_id`. |
| payment_date | DATE | Date the payment attempt was processed. |
| payment_method | STRING | Card, gift_card, wallet, or bank_transfer. |
| payment_status | STRING | succeeded, failed, voided, or refunded. |
| payment_amount | DECIMAL | Amount processed in the payment transaction. |

Primary key: `payment_id`

Foreign key: `order_id` joins to `orders.order_id`

Reporting note: payment success analysis should filter to `payment_status = 'succeeded'`.

## refunds

Refund transaction table. One order can have zero, one, or many refund records.

| Column | Type | Description |
| --- | --- | --- |
| refund_id | STRING | Primary key for a refund transaction. |
| order_id | STRING | Foreign key to `orders.order_id`. |
| refund_date | DATE | Date the refund was processed. |
| refund_reason | STRING | Customer-facing reason such as damaged_item, late_delivery, duplicate_order, or changed_mind. |
| refund_amount | DECIMAL | Refunded amount in USD. |
| refund_status | STRING | completed, pending, or rejected. |

Primary key: `refund_id`

Foreign key: `order_id` joins to `orders.order_id`

Reporting note: Net Revenue subtracts only completed refunds.

## Standard Join Paths

Use these joins for supported SQL:

| Analysis Goal | Join Path |
| --- | --- |
| Customer revenue | `customers.customer_id = orders.customer_id` |
| Product revenue | `orders.order_id = order_items.order_id` and `order_items.product_id = products.product_id` |
| Payment success | `orders.order_id = payments.order_id` |
| Refund analysis | `orders.order_id = refunds.order_id` |

Avoid joining `payments` directly to `refunds` unless the analysis explicitly needs payment and refund transaction details at the order level.
