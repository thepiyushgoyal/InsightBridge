-- Monthly revenue and net revenue.
SELECT
    DATE_TRUNC('month', o.order_date) AS order_month,
    SUM(o.gross_order_amount) AS revenue,
    SUM(o.gross_order_amount) - COALESCE(SUM(r.completed_refund_amount), 0) AS net_revenue
FROM analytics.orders AS o
LEFT JOIN (
    SELECT
        order_id,
        SUM(refund_amount) AS completed_refund_amount
    FROM analytics.refunds
    WHERE refund_status = 'completed'
    GROUP BY order_id
) AS r
    ON o.order_id = r.order_id
WHERE o.order_status <> 'cancelled'
GROUP BY 1
ORDER BY 1;

-- Average order value by month.
SELECT
    DATE_TRUNC('month', order_date) AS order_month,
    SUM(gross_order_amount) / COUNT(DISTINCT order_id) AS average_order_value
FROM analytics.orders
WHERE order_status <> 'cancelled'
GROUP BY 1
ORDER BY 1;

-- Monthly active customers.
SELECT
    DATE_TRUNC('month', o.order_date) AS order_month,
    COUNT(DISTINCT c.customer_id) AS monthly_active_customers
FROM analytics.orders AS o
JOIN analytics.customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status <> 'cancelled'
  AND c.is_duplicate = FALSE
GROUP BY 1
ORDER BY 1;

-- Product revenue by category.
SELECT
    p.category,
    SUM((oi.quantity * oi.unit_price) - oi.item_discount) AS line_revenue
FROM analytics.orders AS o
JOIN analytics.order_items AS oi
    ON o.order_id = oi.order_id
JOIN analytics.products AS p
    ON oi.product_id = p.product_id
WHERE o.order_status <> 'cancelled'
GROUP BY 1
ORDER BY line_revenue DESC;

-- Refund rate by month.
SELECT
    DATE_TRUNC('month', o.order_date) AS order_month,
    1.0 * COUNT(DISTINCT CASE WHEN r.order_id IS NOT NULL THEN o.order_id END)
        / NULLIF(COUNT(DISTINCT o.order_id), 0) AS refund_rate
FROM analytics.orders AS o
LEFT JOIN (
    SELECT DISTINCT order_id
    FROM analytics.refunds
    WHERE refund_status = 'completed'
) AS r
    ON o.order_id = r.order_id
WHERE o.order_status <> 'cancelled'
GROUP BY 1
ORDER BY 1;

-- Payment success rate by payment method.
SELECT
    payment_method,
    1.0 * COUNT(CASE WHEN payment_status = 'succeeded' THEN payment_id END)
        / NULLIF(COUNT(payment_id), 0) AS payment_success_rate
FROM analytics.payments
GROUP BY 1
ORDER BY payment_success_rate DESC;

-- Top products by units sold.
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS quantity_sold
FROM analytics.orders AS o
JOIN analytics.order_items AS oi
    ON o.order_id = oi.order_id
JOIN analytics.products AS p
    ON oi.product_id = p.product_id
WHERE o.order_status <> 'cancelled'
GROUP BY 1, 2
ORDER BY quantity_sold DESC
LIMIT 10;
