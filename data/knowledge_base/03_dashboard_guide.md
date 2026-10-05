# Dashboard Guide

The InsightBridge executive dashboard is designed for weekly and monthly e-commerce performance reviews.

## Executive Summary

The top row should include:

- Revenue
- Net Revenue
- Average Order Value
- Monthly Active Customers
- Refund Rate

Use month-to-date and prior-month comparisons where possible. Label all revenue values in USD.

## Revenue Trend

Revenue and Net Revenue should be shown as monthly line charts. Revenue helps leaders understand gross demand, while Net Revenue shows retained sales after completed refunds.

Dashboard notes:

- Exclude cancelled orders.
- Subtract completed refunds only for Net Revenue.
- Use `DATE_TRUNC('month', orders.order_date)` for monthly reporting.

## Product Performance

Product performance should show Revenue by category, brand, and product. Use the `orders`, `order_items`, and `products` tables.

Recommended fields:

- product_name
- category
- brand
- quantity_sold
- line_revenue

Line revenue is `(order_items.quantity * order_items.unit_price) - order_items.item_discount`.

## Customer Activity

Monthly Active Customers should count unique, non-duplicate customers with at least one non-cancelled order in the month.

The dashboard should separate new customers from returning customers when possible:

- New customer: first non-cancelled order occurred in the selected month.
- Returning customer: first non-cancelled order occurred before the selected month.

## Refund Monitoring

Refund Rate should be monitored by month and by refund reason. Completed refunds are the only refunds included in the KPI. Pending and rejected refunds should be shown in operational drilldowns, not in the executive KPI.

## Conversion Rate Guidance

Conversion Rate can be displayed in the executive dashboard if a trusted sessions data source is available. The current documented analytics warehouse does not include a sessions table, so InsightBridge should not generate Conversion Rate SQL from the documented schema.

When presenting Conversion Rate, include:

- total website sessions
- completed orders
- conversion rate percentage
- date range
- traffic source, when available
