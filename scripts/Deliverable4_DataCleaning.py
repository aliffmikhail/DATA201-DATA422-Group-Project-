"""
===============================================================================
Script      : clean_airbnb_dataset.py
Purpose     : Clean the Christchurch Airbnb listings dataset (Oct 2025 - Jun 2026)
              for downstream analysis. Fills systemic missing values, drops
              redundant columns, removes listings with no price, filters extreme
              price outliers, prints an audit report and writes the cleaned CSV.

Dependencies:
    - Python 3
    - pandas   (third-party: pip install pandas)
    - os       (standard library)

Inputs:
    - FILE_PATH   : data/processed/christchurch_listings_2025_10_to_2026_06.csv
        Required columns:
            id, host_id          -> read as strings (preserves large IDs)
            host_name            -> text
            reviews_per_month    -> numeric
            minimum_nights       -> numeric
            price                -> numeric
        Optional columns (dropped if present):
            license, neighbourhood_group

Outputs:
    - OUTPUT_PATH : data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv
        Same columns as the input minus license / neighbourhood_group, with
        missing values filled, no missing prices, and price <= 1500. Written
        without the pandas index.
    - Console     : load message, data cleaning audit report, save confirmation.

Processing steps:
    1. Load dataset (id / host_id as strings)
    2. Fill missing id / host_id with "Unknown"
    3. Fill host_name ("Unknown"), reviews_per_month (0.0),
       minimum_nights (column median)
    4. Drop license / neighbourhood_group
    5. Drop rows with missing price
    6. Drop rows with price > 1500
    7. Print audit report
    8. Export cleaned CSV

Sanity checks:
    The script stops with a descriptive error (FileNotFoundError, KeyError,
    TypeError or ValueError) if the input is missing, empty, lacks required
    columns, has non-numeric or impossible values, or if any cleaning step
    produces an inconsistent result. Checks never alter the data; for valid
    input the outputs are identical to the unchecked version.
===============================================================================
"""

import os
import pandas as pd

# Define paths
FILE_PATH = "data/processed/christchurch_listings_2025_10_to_2026_06.csv"
OUTPUT_PATH = "data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv"

# Columns the cleaning logic depends on
REQUIRED_COLUMNS = [
    "id",
    "host_id",
    "host_name",
    "reviews_per_month",
    "minimum_nights",
    "price",
]


def _require(condition, message):
    """Raise ValueError with a clear message when a sanity check fails."""
    if not condition:
        raise ValueError(f"Sanity check failed: {message}")


def clean_airbnb_dataset(file_path, output_path):
    # --- Sanity: path arguments ---
    for name, value in (("file_path", file_path), ("output_path", output_path)):
        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"{name} must be a non-empty string, got: {value!r}")
    _require(
        os.path.abspath(file_path) != os.path.abspath(output_path),
        "output_path is the same as file_path; this would overwrite the raw input.",
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find the dataset at: {file_path}")

    # --- Sanity: input is a non-empty file ---
    _require(os.path.isfile(file_path), f"{file_path} is not a file.")
    _require(os.path.getsize(file_path) > 0, f"{file_path} is empty (0 bytes).")

    # 1. Load dataset - Direct string parsing prevents float precision corruption on big IDs
    df = pd.read_csv(file_path, dtype={"id": str, "host_id": str})
    initial_rows = len(df)

    # --- Sanity: dataset has rows and the columns we rely on ---
    # (also guarantees the retention-rate division below never divides by zero)
    _require(initial_rows > 0, f"{file_path} contains a header but no data rows.")
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise KeyError(
            f"Dataset is missing required column(s): {missing_cols}. "
            f"Found columns: {list(df.columns)}"
        )

    # --- Sanity: numeric columns are actually numeric ---
    # (a price like "$120.00" would load as text and break the price filter)
    for col in ("price", "reviews_per_month", "minimum_nights"):
        if not pd.api.types.is_numeric_dtype(df[col]):
            sample = df[col].dropna().head(3).tolist()
            raise TypeError(
                f"Column '{col}' must be numeric but has dtype {df[col].dtype}. "
                f"Sample values: {sample}"
            )

    # --- Sanity: values are physically possible ---
    _require(
        (df["price"].dropna() >= 0).all(),
        f"'price' contains negative values (min = {df['price'].min()}).",
    )
    _require(
        (df["reviews_per_month"].dropna() >= 0).all(),
        f"'reviews_per_month' contains negative values "
        f"(min = {df['reviews_per_month'].min()}).",
    )
    _require(
        (df["minimum_nights"].dropna() >= 1).all(),
        f"'minimum_nights' contains values below 1 "
        f"(min = {df['minimum_nights'].min()}).",
    )

    print(f"🚀 Initial Dataset Loaded: {initial_rows} rows.")

    # 2. Handle missing IDs cleanly without breaking text strings
    df["id"] = df["id"].fillna("Unknown")
    df["host_id"] = df["host_id"].fillna("Unknown")

    # 3. Handle Systemic Missing Values (No Rows Lost)
    df["host_name"] = df["host_name"].fillna("Unknown")
    df["reviews_per_month"] = df["reviews_per_month"].fillna(0.0)

    # Impute missing minimum nights with the median (1.0)
    min_nights_median = df["minimum_nights"].median()

    # --- Sanity: a median exists (fails if the whole column is empty) ---
    _require(
        pd.notna(min_nights_median),
        "'minimum_nights' is entirely missing, so no median can be imputed.",
    )

    df["minimum_nights"] = df["minimum_nights"].fillna(min_nights_median)

    # --- Sanity: filled columns are now complete and no rows were lost ---
    filled_cols = ["id", "host_id", "host_name", "reviews_per_month", "minimum_nights"]
    still_null = {col: int(df[col].isna().sum()) for col in filled_cols if df[col].isna().any()}
    _require(not still_null, f"Missing values remain after filling: {still_null}")
    _require(
        len(df) == initial_rows,
        f"Row count changed during filling ({initial_rows} -> {len(df)}).",
    )

    # 4. Drop Redundant / Constant Columns (No Columns Lost)
    columns_to_drop = ["license", "neighbourhood_group"]
    df = df.drop(
        columns=[col for col in columns_to_drop if col in df.columns],
        errors="ignore",
    )

    # --- Sanity: only the intended columns were dropped ---
    _require(
        not any(col in df.columns for col in columns_to_drop),
        f"Columns {columns_to_drop} are still present after the drop step.",
    )
    _require(
        all(col in df.columns for col in REQUIRED_COLUMNS),
        "A required column was lost during the drop step.",
    )

    # 5. Handle Missing Prices (Rows Lost)
    df_clean = df.dropna(subset=["price"]).copy()
    rows_after_null_drop = len(df_clean)
    null_price_lost = initial_rows - rows_after_null_drop

    # --- Sanity: prices are complete and some rows survived ---
    _require(df_clean["price"].notna().all(), "Missing prices remain after dropna.")
    _require(
        rows_after_null_drop > 0,
        "Every row has a missing price; nothing left to clean.",
    )

    # 6. Filter Extreme Price Outliers / Entry Typos (Rows Lost)
    price_cap = 1500.0
    df_final = df_clean[df_clean["price"] <= price_cap].copy()
    final_rows = len(df_final)
    outliers_lost = rows_after_null_drop - final_rows

    # --- Sanity: filter worked and the row accounting adds up ---
    _require(final_rows > 0, f"No rows left after applying the ${price_cap:,.0f} price cap.")
    _require(
        df_final["price"].max() <= price_cap,
        f"Prices above the cap remain (max = {df_final['price'].max()}).",
    )
    _require(
        null_price_lost >= 0 and outliers_lost >= 0,
        f"Negative row loss computed (missing-price: {null_price_lost}, "
        f"outliers: {outliers_lost}).",
    )
    _require(
        null_price_lost + outliers_lost + final_rows == initial_rows,
        f"Row accounting mismatch: {null_price_lost} + {outliers_lost} + "
        f"{final_rows} != {initial_rows}.",
    )

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

    # --- Sanity: the written file matches what we meant to save ---
    written = pd.read_csv(output_path, dtype={"id": str, "host_id": str})
    _require(
        len(written) == final_rows,
        f"Saved file has {len(written)} rows, expected {final_rows}.",
    )
    _require(
        list(written.columns) == list(df_final.columns),
        "Saved file's columns do not match the cleaned dataset.",
    )

    print(f"💾 Cleaned dataset successfully saved to: {output_path}\n")


if __name__ == "__main__":
    clean_airbnb_dataset(FILE_PATH, OUTPUT_PATH)