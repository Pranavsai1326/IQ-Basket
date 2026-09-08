"""
Load cleaned CSV files into a SQLite database with two tables:
customer_behavior and online_retail.
"""

import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
DB_PATH = os.path.join(BASE_DIR, "ecommerce_analytics.db")


def main():
    customer_df = pd.read_csv(os.path.join(CLEAN_DIR, "customer_shopping_cleaned.csv"))
    retail_df = pd.read_csv(
        os.path.join(CLEAN_DIR, "online_retail_cleaned.csv"),
        parse_dates=["invoice_date"],
        dtype={"invoice_no": str, "stock_code": str},
    )

    conn = sqlite3.connect(DB_PATH)

    customer_df.to_sql("customer_behavior", conn, if_exists="replace", index=False)
    retail_df.to_sql("online_retail", conn, if_exists="replace", index=False)

    print("Database created successfully at:", DB_PATH)
    print("Tables loaded:")
    print("- customer_behavior")
    print("- online_retail")

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customer_behavior;")
    customer_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM online_retail;")
    retail_count = cursor.fetchone()[0]

    print(f"\ncustomer_behavior row count: {customer_count}")
    print(f"online_retail row count: {retail_count}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\nTables in database: {tables}")

    conn.close()


if __name__ == "__main__":
    main()
