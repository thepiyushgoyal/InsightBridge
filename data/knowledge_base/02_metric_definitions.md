# KPI and Metric Definitions

These definitions are the source of truth for InsightBridge e-commerce reporting.

## Revenue

Revenue is the total value of non-cancelled customer orders before refunds.

Formula:

`SUM(orders.gross_order_amount)` where `orders.order_status <> 'cancelled'`

Use Revenue for top-line sales reporting. Do not subtract refunds from Revenue; use Net Revenue when refunds matter.

## Net Revenue

Net Revenue is Revenue minus completed refunds.

Formula:

`SUM(non_cancelled gross_order_amount) - SUM(completed refund_amount)`

Rules:

- Exclude cancelled orders from the order amount.
- Subtract only refunds where `refunds.refund_status = 'completed'`.
- If an order has no refund row, treat refund amount as zero.

## Average Order Value

Average Order Value, or AOV, is the average gross order amount for non-cancelled orders.

Formula:

`SUM(gross_order_amount) / COUNT(DISTINCT order_id)` where `order_status <> 'cancelled'`

Use distinct order count to avoid duplication when joining to order_items or refunds.

## Conversion Rate

Conversion Rate is the share of website sessions that result in a completed order.

Formula:

`completed_orders / website_sessions`

Important limitation: the current documented warehouse tables do not include a sessions table. The dashboard guide may describe how to present Conversion Rate, but SQL for Conversion Rate cannot be produced from the documented schema alone.

## Monthly Active Customer

A Monthly Active Customer is a unique, non-duplicate customer with at least one non-cancelled order in a calendar month.

Formula:

`COUNT(DISTINCT customers.customer_id)` where `customers.is_duplicate = FALSE` and `orders.order_status <> 'cancelled'`

Group by month using `DATE_TRUNC('month', orders.order_date)`.

## Refund Rate

Refund Rate is the percentage of non-cancelled orders that had at least one completed refund.

Formula:

`COUNT(DISTINCT refunded_order_id) / COUNT(DISTINCT non_cancelled_order_id)`

Rules:

- The denominator excludes cancelled orders.
- The numerator includes orders with at least one refund where `refund_status = 'completed'`.
- Count each order once even if it has multiple refund rows.

## Churn

Churn is a customer retention metric based on purchasing inactivity.

Definition:

A customer is considered churned in a reporting month if they were active in a previous month but have no non-cancelled order in the following 90 days.

Rules:

- Use non-cancelled orders only.
- Exclude duplicate customer records.
- Churn is best reported as a cohort or retention analysis, not as a simple order-level metric.
