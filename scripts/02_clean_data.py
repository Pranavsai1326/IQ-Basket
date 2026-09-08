"""
Clean the two raw datasets independently and save clean CSVs.

Customer Shopping Trends columns are renamed to clean snake_case names
for consistency in the database/SQL layer. Note: this dataset has no
purchase-date column in its real schema, so no date cleaning is done
for it.
"""

import os

import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)


def clean_customer_shopping():
    print("=" * 60)
    print("CLEANING: CUSTOMER SHOPPING TRENDS")
    print("=" * 60)

    df = pd.read_csv(os.path.join(RAW_DIR, "customer_shopping_trends.csv"))
    original_rows = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = original_rows - len(df)

    # Rename to clean, explicit column names used across DB/SQL/dashboard
    df = df.rename(
        columns={
            "Customer ID": "customer_id",
            "Age": "age",
            "Gender": "gender",
            "Item Purchased": "item_purchased",
            "Category": "product_category",
            "Purchase Amount (USD)": "purchase_amount",
            "Location": "location",
            "Size": "size",
            "Color": "color",
            "Season": "season",
            "Review Rating": "review_rating",
            "Subscription Status": "subscription_status",
            "Payment Method": "payment_method",
            "Shipping Type": "shipping_type",
            "Discount Applied": "discount_applied",
            "Promo Code Used": "promo_code_used",
            "Previous Purchases": "previous_purchases",
            "Preferred Payment Method": "preferred_payment_method",
            "Frequency of Purchases": "frequency_of_purchases",
        }
    )

    # Gender: fill missing with "Unknown"
    df["gender"] = df["gender"].fillna("Unknown").astype(str).str.strip()

    # Purchase amount: numeric, remove <= 0
    df["purchase_amount"] = pd.to_numeric(df["purchase_amount"], errors="coerce")
    before = len(df)
    df = df[df["purchase_amount"] > 0]
    invalid_amount_removed = before - len(df)

    # Age: keep valid reasonable range 18-100, drop rows outside/non-numeric
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    before = len(df)
    df = df[(df["age"] >= 18) & (df["age"] <= 100)]
    invalid_age_removed = before - len(df)

    # Strip whitespace on key string/categorical fields
    for col in ["location", "product_category", "payment_method", "frequency_of_purchases"]:
        df[col] = df[col].astype(str).str.strip()

    df = df.dropna(subset=["purchase_amount", "age"])

    final_rows = len(df)

    print(f"Original rows: {original_rows}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Invalid purchase_amount rows removed: {invalid_amount_removed}")
    print(f"Invalid age rows removed: {invalid_age_removed}")
    print(f"Final rows: {final_rows}\n")

    out_path = os.path.join(CLEAN_DIR, "customer_shopping_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved -> {out_path}\n")
    return df


def clean_online_retail():
    print("=" * 60)
    print("CLEANING: ONLINE RETAIL")
    print("=" * 60)

    df = pd.read_csv(os.path.join(RAW_DIR, "online_retail.csv"))
    original_rows = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = original_rows - len(df)

    # Quantity: numeric, remove <= 0 (cancellations/returns)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    before = len(df)
    df = df[df["Quantity"] > 0]
    invalid_quantity_removed = before - len(df)

    # UnitPrice: numeric, remove <= 0
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    before = len(df)
    df = df[df["UnitPrice"] > 0]
    invalid_price_removed = before - len(df)

    # Revenue
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    # InvoiceDate: convert to datetime, drop rows where conversion fails
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["InvoiceDate"])
    invalid_date_removed = before - len(df)

    # Strip whitespace on string fields
    for col in ["InvoiceNo", "StockCode", "Description", "Country"]:
        df[col] = df[col].astype(str).str.strip()

    # Keep missing CustomerID rows (still useful for transaction/revenue
    # analysis); they are simply excluded later when counting unique
    # customers.
    missing_customer_ids = df["CustomerID"].isnull().sum()

    # Rename to clean snake_case names for the database layer
    df = df.rename(
        columns={
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
            "Revenue": "revenue",
        }
    )

    final_rows = len(df)

    print(f"Original rows: {original_rows}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Invalid quantity (<=0) rows removed: {invalid_quantity_removed}")
    print(f"Invalid unit_price (<=0) rows removed: {invalid_price_removed}")
    print(f"Invalid invoice_date rows removed: {invalid_date_removed}")
    print(f"Rows kept with missing customer_id (used for revenue, excluded from customer counts): {missing_customer_ids}")
    print(f"Final rows: {final_rows}\n")

    out_path = os.path.join(CLEAN_DIR, "online_retail_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved -> {out_path}\n")
    return df


if __name__ == "__main__":
    clean_customer_shopping()
    clean_online_retail()
