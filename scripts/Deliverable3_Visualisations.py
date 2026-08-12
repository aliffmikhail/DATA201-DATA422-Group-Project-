import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG - adjust these paths/column names to match your actual data
# ---------------------------------------------------------------------------
NZ_WIDE_PATH = "data/raw/listings.csv"
CHRISTCHURCH_PATH = "data/processed/christchurch_listings_2025_10_to_2026_06.csv"

PRICE_COL = "price"
REVIEWS_COL = "number_of_reviews"
LAST_REVIEW_COL = "last_review"
CITY_COL = "neighbourhood_group"       # or "city" depending on your dataset
CHRISTCHURCH_LABEL = "Christchurch City"  # UPDATE: exact string used in your data

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helper: clean price column ($ and commas -> float)
# ---------------------------------------------------------------------------
def clean_price(df, col=PRICE_COL):
    if df[col].dtype == object:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Step 1: Load datasets
# ---------------------------------------------------------------------------
print("Loading datasets...")

nz_df = pd.read_csv(NZ_WIDE_PATH)
chc_df = pd.read_csv(CHRISTCHURCH_PATH)

print(f"NZ-wide dataset: {len(nz_df):,} rows")
print(f"Christchurch dataset: {len(chc_df):,} rows")

# ---------------------------------------------------------------------------
# Step 2: Clean price columns
# ---------------------------------------------------------------------------
nz_df = clean_price(nz_df)
chc_df = clean_price(chc_df)

# ---------------------------------------------------------------------------
# Step 3: Price histograms
# ---------------------------------------------------------------------------
print("Generating price histograms...")

plt.figure(figsize=(8, 5))
nz_df[PRICE_COL].dropna().plot(kind="hist", bins=50, edgecolor="black")
plt.title("New Zealand Airbnb Price Distribution")
plt.xlabel("Price ($)")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "nz_price_histogram.png")
plt.close()

plt.figure(figsize=(8, 5))
chc_df[PRICE_COL].dropna().plot(kind="hist", bins=50, edgecolor="black", color="orange")
plt.title("Christchurch City Airbnb Price Distribution")
plt.xlabel("Price ($)")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "christchurch_price_histogram.png")
plt.close()

plt.figure(figsize=(8, 5))
plt.hist(nz_df[PRICE_COL].dropna(), bins=50, alpha=0.5, label="New Zealand")
plt.hist(chc_df[PRICE_COL].dropna(), bins=50, alpha=0.5, label="Christchurch City")
plt.title("NZ vs Christchurch Airbnb Price Distribution")
plt.xlabel("Price ($)")
plt.ylabel("Number of Listings")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "nz_vs_christchurch_price_histogram.png")
plt.close()

print("Price histograms saved.")

# ---------------------------------------------------------------------------
# Step 4: days_since_last_review
# ---------------------------------------------------------------------------
print("Calculating days_since_last_review...")

REFERENCE_DATE = pd.Timestamp(datetime.today().date())

chc_df[LAST_REVIEW_COL] = pd.to_datetime(chc_df[LAST_REVIEW_COL], errors="coerce")
chc_df["days_since_last_review"] = (REFERENCE_DATE - chc_df[LAST_REVIEW_COL]).dt.days

plt.figure(figsize=(8, 5))
chc_df["days_since_last_review"].dropna().plot(kind="hist", bins=50, edgecolor="black", color="green")
plt.title("Days Since Last Review - Christchurch City")
plt.xlabel("Days Since Last Review")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "days_since_last_review_histogram.png")
plt.close()

print("days_since_last_review plot saved.")

# ---------------------------------------------------------------------------
# Step 5: Top 10% of listings by number_of_reviews
# ---------------------------------------------------------------------------
print("Calculating top 10% listings by number_of_reviews...")

threshold = nz_df[REVIEWS_COL].quantile(0.90)
top_10_pct = nz_df[nz_df[REVIEWS_COL] >= threshold]

print(f"Top 10% threshold (number_of_reviews): {threshold}")
print(f"Number of listings in top 10%: {len(top_10_pct)}")

if CITY_COL in top_10_pct.columns:
    chc_count = (top_10_pct[CITY_COL] == CHRISTCHURCH_LABEL).sum()
    print(f"Of those, {chc_count} are located in {CHRISTCHURCH_LABEL}")
else:
    print(f"Column '{CITY_COL}' not found - update CITY_COL in CONFIG section.")

# ---------------------------------------------------------------------------
# Step 6: Sanity checks
# ---------------------------------------------------------------------------
print("\n--- Sanity Checks ---")
print(f"NZ price range: {nz_df[PRICE_COL].min()} - {nz_df[PRICE_COL].max()}")
print(f"Christchurch price range: {chc_df[PRICE_COL].min()} - {chc_df[PRICE_COL].max()}")
print(f"Missing values in days_since_last_review: {chc_df['days_since_last_review'].isna().sum()}")
print("Plots saved to:", OUTPUT_DIR.resolve())
print("Done.")