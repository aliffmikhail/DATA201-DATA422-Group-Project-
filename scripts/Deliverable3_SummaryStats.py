import pandas as pd
from tabulate import tabulate

# Load the combined Christchurch dataset
file_path = "data/processed/christchurch_listings_2025_10_to_2026_06.csv"
df = pd.read_csv(file_path)

# ==========================================
# 1. CORE DATASET METRICS
# ==========================================
print("=" * 50)
print(" 🏢 CHRISTCHURCH DATASET OVERVIEW ")
print("=" * 50)
print(f"🔹 Total Rows (Listings): {df.shape[0]:,}")
print(f"🔹 Total Columns (Features): {df.shape[1]}")
print("-" * 50)

# ==========================================
# 2. COLUMN DATA TYPES TABLE
# ==========================================
print("\n📋 COLUMN DATA TYPES:")
dtype_df = pd.DataFrame({"Data Type": df.dtypes}).reset_index()
dtype_df.columns = ["Column Name", "Data Type"]
print(tabulate(dtype_df, headers="keys", tablefmt="round", showindex=False))
print("-" * 50)

# ==========================================
# 3. NUMERICAL SUMMARY STATISTICS
# ==========================================
print("\n📊 NUMERICAL SUMMARY STATISTICS:")
# Transposing (.T) makes long tables fit perfectly on presentation slides
summary_df = df.describe().T.reset_index()
summary_df.columns = [
    "Metric",
    "Count",
    "Mean",
    "Std Dev",
    "Min",
    "25%",
    "50% (Med)",
    "75%",
    "Max",
]
# Rounding values makes numbers immediately readable
print(
    tabulate(
        summary_df.round(2), headers="keys", tablefmt="round", showindex=False
    )
)
print("-" * 50)

# ==========================================
# 4. MISSING VALUES ANALYSIS
# ==========================================
print("\n⚠️ MISSING VALUES ANALYSIS:")
missing_count = df.isna().sum()
missing_pct = (df.isna().sum() / len(df)) * 100
missing_df = pd.DataFrame(
    {"Missing Count": missing_count, "Missing %": missing_pct}
).reset_index()
missing_df.columns = ["Column Name", "Missing Count", "Missing %"]

# Only show columns that actually have missing data to reduce slide clutter
missing_df = missing_df[missing_df["Missing Count"] > 0]

if missing_df.empty:
    print("✅ Perfect! No missing values found in the dataset.")
else:
    print(
        tabulate(
            missing_df.round(1),
            headers="keys",
            tablefmt="round",
            showindex=False,
        )
    )
print("-" * 50)

# ==========================================
# 5. CATEGORICAL COLUMNS SUMMARY
# ==========================================
print("\n🗂️ CATEGORICAL VALUE COUNTS:")
categorical_columns = df.select_dtypes(include=["object"]).columns

for column in categorical_columns:
    print(f"\n🔹 Feature: {column.upper()}")
    counts = df[column].value_counts(dropna=False).reset_index()
    counts.columns = ["Value", "Count"]
    # Limit to top 10 unique values so console doesn't overflow
    print(tabulate(counts.head(10), headers="keys", tablefmt="simple"))
print("=" * 50)

# ==========================================
# PRICE SUMMARY STATISTICS
# ==========================================
print("\n💰 PROPERTY PRICE ANALYSIS:")

# Change "price" to match the exact capitalisation of column name
price_col = "price" 

if price_col in df.columns:
    # Calculate specific presentation-friendly metrics
    price_stats = {
        "Metric": [
            "Minimum Price", 
            "25th Percentile (Low End)", 
            "Median Price (Typical)", 
            "75th Percentile (High End)", 
            "Maximum Price", 
            "Average Price"
        ],
        "Value": [
            f"${df[price_col].min():,.2f}",
            f"${df[price_col].quantile(0.25):,.2f}",
            f"${df[price_col].median():,.2f}",
            f"${df[price_col].quantile(0.75):,.2f}",
            f"${df[price_col].max():,.2f}",
            f"${df[price_col].mean():,.2f}"
        ]
    }
    price_df = pd.DataFrame(price_stats)
    print(tabulate(price_df, headers="keys", tablefmt="rounded_grid", showindex=False))
else:
    print(f"⚠️ Warning: '{price_col}' column not found. Check your column names!")
print("-" * 50)
