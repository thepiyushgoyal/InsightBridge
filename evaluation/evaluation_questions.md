# Evaluation Questions

Use these questions to manually check whether InsightBridge retrieves the right sources and stays grounded.

| # | Question | Expected Source Documents |
| --- | --- | --- |
| 1 | What columns are available in the `orders` table? | `01_data_dictionary.md` |
| 2 | Which table contains refund reasons? | `01_data_dictionary.md` |
| 3 | How do I join orders to products? | `01_data_dictionary.md`, `03_dashboard_guide.md` |
| 4 | What is the difference between Revenue and Net Revenue? | `02_metric_definitions.md` |
| 5 | How should Average Order Value be calculated? | `02_metric_definitions.md` |
| 6 | Can you generate SQL for Conversion Rate? | `02_metric_definitions.md`, `03_dashboard_guide.md` |
| 7 | What is a Monthly Active Customer? | `02_metric_definitions.md` |
| 8 | What data-quality filters should I apply to customer metrics? | `05_data_quality_rules.md`, `02_metric_definitions.md` |
| 9 | Write a SQL query for monthly active customers. | `04_sql_examples.sql`, `02_metric_definitions.md` |
| 10 | Write a SQL query for product revenue by category. | `04_sql_examples.sql`, `01_data_dictionary.md` |
| 11 | How is Refund Rate calculated? | `02_metric_definitions.md`, `05_data_quality_rules.md` |
| 12 | Why should cancelled orders be excluded from revenue? | `05_data_quality_rules.md`, `02_metric_definitions.md` |
| 13 | What should the executive dashboard show in the top row? | `03_dashboard_guide.md` |
| 14 | What products are in the sample catalog? | `product_catalog.csv` |
| 15 | Write a SQL query to delete cancelled orders. | Prompt should refuse because only read-only SELECT SQL is allowed; supporting context from `05_data_quality_rules.md` |
| 16 | Show monthly net revenue and run the query. | `06_sqlite_execution_notes.md`, `04_sql_examples.sql`, `02_metric_definitions.md` |
| 17 | Show top products by units sold. | `06_sqlite_execution_notes.md`, `04_sql_examples.sql` |
| 18 | Show monthly active customers using SQLite syntax. | `06_sqlite_execution_notes.md`, `02_metric_definitions.md` |
