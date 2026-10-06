from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "christchurch_listings_combined.csv"

# Matches only monthly files like christchurch_2026_07.csv.
# The combined files (christchurch_listings_...) don't match this pattern.
monthly_files = sorted(
    f for f in PROCESSED_DIR.glob("christchurch_????_??.csv")
    if f != OUTPUT_FILE
)

if not monthly_files:
    raise FileNotFoundError("No monthly Christchurch files found.")

frames = [pd.read_csv(f) for f in monthly_files]
combined = pd.concat(frames, ignore_index=True)
combined.to_csv(OUTPUT_FILE, index=False)

print(f"Combined {len(monthly_files)} monthly files")
print(f"Rows: {len(combined):,}")
print(f"Saved: {OUTPUT_FILE}")