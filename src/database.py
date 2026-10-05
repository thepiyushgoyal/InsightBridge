from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_PATH = ROOT_DIR / "data" / "sample_database" / "ecommerce.db"


def initialize_sample_database(db_path: Path = DEFAULT_DATABASE_PATH) -> Path:
    """Create a small local SQLite database for SQL execution demos."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS refunds;
            DROP TABLE IF EXISTS payments;
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS customers;

            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                email TEXT,
                first_order_date TEXT,
                signup_date TEXT,
                country TEXT,
                acquisition_channel TEXT,
                is_duplicate INTEGER
            );

            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                order_date TEXT,
                order_status TEXT,
                gross_order_amount REAL,
                currency TEXT,
                promo_code TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                category TEXT,
                brand TEXT,
                list_price REAL,
                active_flag INTEGER
            );

            CREATE TABLE order_items (
                order_item_id TEXT PRIMARY KEY,
                order_id TEXT,
                product_id TEXT,
                quantity INTEGER,
                unit_price REAL,
                item_discount REAL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );

            CREATE TABLE payments (
                payment_id TEXT PRIMARY KEY,
                order_id TEXT,
                payment_date TEXT,
                payment_method TEXT,
                payment_status TEXT,
                payment_amount REAL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE refunds (
                refund_id TEXT PRIMARY KEY,
                order_id TEXT,
                refund_date TEXT,
                refund_reason TEXT,
                refund_amount REAL,
                refund_status TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );
            """
        )

        conn.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("C001", "ana@example.com", "2024-01-05", "2023-12-22", "US", "paid_search", 0),
                ("C002", "ben@example.com", "2024-01-14", "2024-01-10", "US", "organic", 0),
                ("C003", "chen@example.com", "2024-02-03", "2024-01-28", "CA", "email", 0),
                ("C004", "dia@example.com", "2024-02-17", "2024-02-12", "US", "referral", 0),
                ("C005", "eli@example.com", "2024-03-02", "2024-02-25", "GB", "paid_social", 0),
                ("C006", "ana.dup@example.com", "2024-01-05", "2024-03-08", "US", "paid_search", 1),
                ("C007", "fatima@example.com", "2024-04-01", "2024-03-20", "US", "organic", 0),
                ("C008", "gabe@example.com", "2024-04-22", "2024-04-19", "CA", "email", 0),
            ],
        )

        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("P1001", "Everyday Cotton Tee", "Apparel", "Northstar Basics", 24.00, 1),
                ("P1002", "Trail Runner Sneaker", "Apparel", "StrideWorks", 89.00, 1),
                ("P1003", "Ceramic Pour-Over Set", "Home", "BrewNest", 42.50, 1),
                ("P1004", "LED Desk Lamp", "Home", "LumaDesk", 56.00, 1),
                ("P1005", "Hydrating Face Serum", "Beauty", "GlowTheory", 34.00, 1),
                ("P1006", "Wireless Earbuds", "Electronics", "SoundPilot", 79.99, 1),
                ("P1007", "Canvas Weekend Tote", "Accessories", "HarborLine", 48.00, 0),
                ("P1008", "Stainless Travel Mug", "Home", "BrewNest", 28.00, 1),
            ],
        )

        conn.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("O1001", "C001", "2024-01-05", "completed", 72.00, "USD", "WELCOME10"),
                ("O1002", "C002", "2024-01-14", "completed", 131.50, "USD", None),
                ("O1003", "C001", "2024-02-04", "completed", 89.00, "USD", None),
                ("O1004", "C003", "2024-02-12", "cancelled", 56.00, "USD", None),
                ("O1005", "C004", "2024-02-17", "completed", 113.99, "USD", "FEB15"),
                ("O1006", "C005", "2024-03-02", "returned", 124.00, "USD", None),
                ("O1007", "C002", "2024-03-21", "completed", 42.50, "USD", None),
                ("O1008", "C007", "2024-04-01", "completed", 76.00, "USD", "SPRING"),
                ("O1009", "C008", "2024-04-22", "pending", 79.99, "USD", None),
                ("O1010", "C004", "2024-04-28", "completed", 48.00, "USD", None),
            ],
        )

        conn.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("OI001", "O1001", "P1001", 3, 24.00, 0.00),
                ("OI002", "O1002", "P1003", 1, 42.50, 0.00),
                ("OI003", "O1002", "P1002", 1, 89.00, 0.00),
                ("OI004", "O1003", "P1002", 1, 89.00, 0.00),
                ("OI005", "O1004", "P1004", 1, 56.00, 0.00),
                ("OI006", "O1005", "P1005", 1, 34.00, 0.00),
                ("OI007", "O1005", "P1006", 1, 79.99, 0.00),
                ("OI008", "O1006", "P1007", 2, 48.00, 0.00),
                ("OI009", "O1006", "P1008", 1, 28.00, 0.00),
                ("OI010", "O1007", "P1003", 1, 42.50, 0.00),
                ("OI011", "O1008", "P1001", 2, 24.00, 0.00),
                ("OI012", "O1008", "P1008", 1, 28.00, 0.00),
                ("OI013", "O1009", "P1006", 1, 79.99, 0.00),
                ("OI014", "O1010", "P1007", 1, 48.00, 0.00),
            ],
        )

        conn.executemany(
            "INSERT INTO payments VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("PAY001", "O1001", "2024-01-05", "card", "succeeded", 72.00),
                ("PAY002", "O1002", "2024-01-14", "wallet", "succeeded", 131.50),
                ("PAY003", "O1003", "2024-02-04", "card", "succeeded", 89.00),
                ("PAY004", "O1004", "2024-02-12", "card", "voided", 56.00),
                ("PAY005", "O1005", "2024-02-17", "gift_card", "succeeded", 113.99),
                ("PAY006", "O1006", "2024-03-02", "card", "succeeded", 124.00),
                ("PAY007", "O1007", "2024-03-21", "wallet", "succeeded", 42.50),
                ("PAY008", "O1008", "2024-04-01", "card", "succeeded", 80.00),
                ("PAY009", "O1009", "2024-04-22", "bank_transfer", "failed", 79.99),
                ("PAY010", "O1010", "2024-04-28", "card", "succeeded", 48.00),
            ],
        )

        conn.executemany(
            "INSERT INTO refunds VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("R001", "O1003", "2024-02-09", "changed_mind", 20.00, "completed"),
                ("R002", "O1006", "2024-03-10", "damaged_item", 48.00, "completed"),
                ("R003", "O1006", "2024-03-12", "late_delivery", 28.00, "completed"),
                ("R004", "O1008", "2024-04-04", "duplicate_order", 10.00, "pending"),
                ("R005", "O1010", "2024-05-02", "changed_mind", 48.00, "rejected"),
            ],
        )

    return db_path
