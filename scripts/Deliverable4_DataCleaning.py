import os
import pandas as pd

# Define paths
FILE_PATH = "data/processed/christchurch_listings_2025_10_to_2026_06.csv"
OUTPUT_PATH = "data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv"


def clean_airbnb_dataset(file_path, output_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find the dataset at: {file_path}")

    # 1. Load dataset - Direct string parsing prevents float precision corruption on big IDs
    df = pd.read_csv(file_path, dtype={"id": str, "host_id": str})
    initial_rows = len(df)
    print(f"🚀 Initial Dataset Loaded: {initial_rows} rows.")

    # 2. Handle missing IDs cleanly without breaking text strings
    df["id"] = df["id"].fillna("Unknown")
    df["host_id"] = df["host_id"].fillna("Unknown")

    # 3. Handle Systemic Missing Values (No Rows Lost)
    df["host_name"] = df["host_name"].fillna("Unknown")
    df["reviews_per_month"] = df["reviews_per_month"].fillna(0.0)

    # Impute missing minimum nights with the median (1.0)
    min_nights_median = df["minimum_nights"].median()
    df["minimum_nights"] = df["minimum_nights"].fillna(min_nights_median)

    # 4. Drop Redundant / Constant Columns (No Columns Lost)
    columns_to_drop = ["license", "neighbourhood_group"]
    df = df.drop(
        columns=[col for col in columns_to_drop if col in df.columns],
        errors="ignore",
    )

    # 5. Handle Missing Prices (Rows Lost)
    df_clean = df.dropna(subset=["price"]).copy()
    rows_after_null_drop = len(df_clean)
    null_price_lost = initial_rows - rows_after_null_drop

    # 6. Filter Extreme Price Outliers / Entry Typos (Rows Lost)
    price_cap = 1500.0
    df_final = df_clean[df_clean["price"] <= price_cap].copy()
    final_rows = len(df_final)
    outliers_lost = rows_after_null_drop - final_rows


    # 7. Print Executed Decisions Log
    print("\n" + "=" * 50)
    print("📊 DATA CLEANING AUDIT REPORT")
    print("=" * 50)
    print(f"Starting Rows:               {initial_rows}")
    print(f"Rows Lost (Missing Prices): -{null_price_lost} (Includes 100% of Dec, Jan, Feb)")
    print(f"Rows Lost (Prices > ${price_cap:,.0f}): -{outliers_lost}")
    print("-" * 50)
    print(f"Final Cleaned Rows:          {final_rows}")
    print(f"Total Data Retention Rate:   {(final_rows / initial_rows) * 100:.2f}%")
    print("=" * 50)

    # 8. Export Cleaned Dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final.to_csv(output_path, index=False)
    print(f"💾 Cleaned dataset successfully saved to: {output_path}\n")


if __name__ == "__main__":
    clean_airbnb_dataset(FILE_PATH, OUTPUT_PATH)
