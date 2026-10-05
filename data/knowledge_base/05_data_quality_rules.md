# Data Quality Rules

These rules should be applied before using InsightBridge metrics in dashboards, analysis, or SQL examples.

## Cancelled Orders

Cancelled orders must be excluded from Revenue, Net Revenue, AOV, Monthly Active Customers, Refund Rate, product revenue, and units sold.

Standard filter:

`orders.order_status <> 'cancelled'`

## Duplicate Customer IDs

Customer-level metrics should exclude duplicate customer profiles.

Standard filter:

`customers.is_duplicate = FALSE`

This applies to Monthly Active Customers, churn analysis, customer retention, and customer segmentation.

## Refund Handling

Only completed refunds should affect financial KPIs.

Standard filter:

`refunds.refund_status = 'completed'`

Pending refunds may be useful for operations, but they should not reduce Net Revenue until completed. Rejected refunds should not reduce Net Revenue.

## Order Item Duplication

Joining `orders` to `order_items` can duplicate order-level values such as `gross_order_amount`. When calculating order-level KPIs after joining to line items, use `COUNT(DISTINCT orders.order_id)` and avoid summing `gross_order_amount` at the duplicated line-item grain.

For product revenue, use line-item revenue:

`(order_items.quantity * order_items.unit_price) - order_items.item_discount`

## Multiple Refund Rows

An order can have multiple refund rows. Refund Rate should count a refunded order once, even if it has several completed refunds.

Use a distinct order-level refund subquery before joining refunds to orders.

## Currency

Executive reporting assumes USD. If future data includes multiple currencies, revenue metrics must be converted to USD before aggregation. The current sample warehouse does not document an exchange-rate table.

## Missing Product Records

If an `order_items.product_id` does not match a product in `products`, product-level dashboard rows should label the product as unknown rather than dropping the order item from financial reporting.
