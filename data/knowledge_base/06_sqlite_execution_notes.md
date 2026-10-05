# SQLite Execution Notes

InsightBridge includes a local SQLite sample database for portfolio demos. The database is stored at `data/sample_database/ecommerce.db` after it is created from the Streamlit sidebar.

## Executable Table Names

When writing SQL that should run in the local demo app, use these SQLite table names without the `analytics.` schema prefix:

- `customers`
- `orders`
- `order_items`
- `products`
- `payments`
- `refunds`

## SQLite Date Handling

The warehouse examples use `DATE_TRUNC('month', date_column)`. SQLite does not support `DATE_TRUNC`.

For monthly grouping in the local demo database, use:

`strftime('%Y-%m', date_column)`

Example:

```sql
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    SUM(gross_order_amount) AS revenue
FROM orders
WHERE order_status <> 'cancelled'
GROUP BY 1
ORDER BY 1;
```

## Local SQL Safety Rules

The app should execute only read-only SQL. Runnable queries must start with `SELECT` or a read-only `WITH` common table expression.

Do not execute statements that modify data or schema, including:

- `INSERT`
- `UPDATE`
- `DELETE`
- `MERGE`
- `DROP`
- `ALTER`
- `CREATE`
- `TRUNCATE`
- `REPLACE`
- `PRAGMA`

## Runnable Example: Monthly Net Revenue

```sql
SELECT
    strftime('%Y-%m', o.order_date) AS order_month,
    SUM(o.gross_order_amount) AS revenue,
    SUM(o.gross_order_amount) - COALESCE(SUM(r.completed_refund_amount), 0) AS net_revenue
FROM orders AS o
LEFT JOIN (
    SELECT
        order_id,
        SUM(refund_amount) AS completed_refund_amount
    FROM refunds
    WHERE refund_status = 'completed'
    GROUP BY order_id
) AS r
    ON o.order_id = r.order_id
WHERE o.order_status <> 'cancelled'
GROUP BY 1
ORDER BY 1;
```

## Runnable Example: Monthly Active Customers

```sql
SELECT
    strftime('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT c.customer_id) AS monthly_active_customers
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status <> 'cancelled'
  AND c.is_duplicate = 0
GROUP BY 1
ORDER BY 1;
```

## Runnable Example: Top Products

```sql
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS quantity_sold
FROM orders AS o
JOIN order_items AS oi
    ON o.order_id = oi.order_id
JOIN products AS p
    ON oi.product_id = p.product_id
WHERE o.order_status <> 'cancelled'
GROUP BY 1, 2
ORDER BY quantity_sold DESC
LIMIT 10;
```
