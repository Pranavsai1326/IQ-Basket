"""
Load both Kaggle datasets via KaggleHub, inspect their real schemas,
and save raw copies locally for lineage/reproducibility.
"""

import os
import shutil

import kagglehub
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def find_csv(download_path, preferred_name=None):
    """Pick the correct CSV inside a KaggleHub download folder."""
    csv_files = [f for f in os.listdir(download_path) if f.lower().endswith(".csv")]
    if preferred_name and preferred_name in csv_files:
        return os.path.join(download_path, preferred_name)
    return os.path.join(download_path, csv_files[0])


def inspect_dataset(name, df):
    print("=" * 60)
    print(name)
    print("=" * 60)
    print("\nRows:", df.shape[0])
    print("Columns:", df.shape[1])
    print("\nColumn Names:")
    print(df.columns.tolist())
    print("\nData Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nDuplicate Rows:", df.duplicated().sum())
    print("\nFirst 5 Rows:")
    print(df.head())
    print()


def main():
    # --- Dataset 1: Customer Shopping Trends ---
    shopping_path = kagglehub.dataset_download(
        "iamsouravbanerjee/customer-shopping-trends-dataset"
    )
    shopping_csv = find_csv(shopping_path, preferred_name="shopping_trends.csv")
    df_shopping = pd.read_csv(shopping_csv)
    inspect_dataset("CUSTOMER SHOPPING TRENDS DATASET", df_shopping)

    shopping_raw_out = os.path.join(RAW_DIR, "customer_shopping_trends.csv")
    shutil.copy(shopping_csv, shopping_raw_out)
    print(f"Saved raw copy -> {shopping_raw_out}\n")

    # --- Dataset 2: Online Retail ---
    retail_path = kagglehub.dataset_download("vijayuv/onlineretail")
    retail_csv = find_csv(retail_path, preferred_name="OnlineRetail.csv")
    df_retail = pd.read_csv(retail_csv, encoding="latin1")
    inspect_dataset("ONLINE RETAIL DATASET", df_retail)

    retail_raw_out = os.path.join(RAW_DIR, "online_retail.csv")
    df_retail.to_csv(retail_raw_out, index=False)
    print(f"Saved raw copy -> {retail_raw_out}\n")

    print("NOTE: The Customer Shopping Trends dataset has NO purchase-date")
    print("column in its actual schema, so date-based analysis (monthly")
    print("trend) is only produced for the Online Retail dataset.")


if __name__ == "__main__":
    main()
