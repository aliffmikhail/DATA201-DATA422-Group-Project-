import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Only match monthly files like listings_2026_07.csv
# (this ignores the NZ-wide listings.csv)
pattern = re.compile(r"listings_(\d{4})_(\d{2})\.csv$")

REQUIRED_COLUMNS = {"id", "latitude", "longitude", "neighbourhood_group"}

raw_files = sorted(RAW_DIR.glob("listings_*.csv"))

for raw_file in raw_files:
    match = pattern.match(raw_file.name)
    if not match:
        continue

    year, month = match.groups()
    month_year = f"{year}-{month}"
    output_path = PROCESSED_DIR / f"christchurch_{year}_{month}.csv"

    # Skip months that are already processed
    if output_path.exists():
        print(f"Skipping existing: {output_path}")
        continue

    # Load monthly dataset
    df = pd.read_csv(raw_file)

    # Stop with a clear error if a required column is missing
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"{raw_file} is missing columns: {sorted(missing)}")

    # Filter to Christchurch City only
    christchurch = df[
        df["neighbourhood_group"] == "Christchurch City"
    ].copy()

    # Reset row numbers after filtering
    christchurch = christchurch.reset_index(drop=True)

    # Add month and year
    christchurch["month_year"] = month_year

    # Save processed Christchurch dataset
    christchurch.to_csv(output_path, index=False)

    # Show how many Christchurch listings were found
    print(f"Created {output_path}: {month_year}, {christchurch.shape}")