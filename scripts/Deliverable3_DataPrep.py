import os
import pandas as pd

# Create processed data folder if it does not already exist
os.makedirs("data/processed", exist_ok=True)

# Monthly Airbnb listings files
files = {
    "2025-10": "data/raw/listings_2025_10.csv",
    "2025-11": "data/raw/listings_2025_11.csv",
    "2025-12": "data/raw/listings_2025_12.csv",
    "2026-01": "data/raw/listings_2026_01.csv",
    "2026-02": "data/raw/listings_2026_02.csv",
    "2026-03": "data/raw/listings_2026_03.csv",
    "2026-04": "data/raw/listings_2026_04.csv",
    "2026-05": "data/raw/listings_2026_05.csv",
    "2026-06": "data/raw/listings_2026_06.csv"
}

for month_year, file_path in files.items():

    # Load monthly dataset
    df = pd.read_csv(file_path)

    # Filter to Christchurch City only
    christchurch = df[
        df["neighbourhood_group"] == "Christchurch City"
    ].copy()

    # Reset row numbers after filtering
    christchurch = christchurch.reset_index(drop=True)

    # Add month and year
    christchurch["month_year"] = month_year

     # Create output filename
    output_path = (
        f"data/processed/christchurch_"
        f"{month_year.replace('-', '_')}.csv"
    )

    # Save processed Christchurch dataset
    christchurch.to_csv(output_path, index=False)

    # Show how many Christchurch listings were found
    print(month_year, christchurch.shape)