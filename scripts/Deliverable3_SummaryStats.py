import pandas as pd
# Load the combined Christchurch dataset
df = pd.read_csv(
"data/processed/christchurch_listings_2025_10_to_2026_06.csv"
)
# Basic dataset information
print("Dataset shape:")
print(df.shape)
print("\nColumn data types:")
print(df.dtypes)
# Numerical summary statistics
# Select numerical columns
numeric_columns = df.select_dtypes(include="number").columns

# Remove identifier columns and license because these do not have
# meaningful numerical summary statistics
numeric_columns = numeric_columns.drop(
    ["id", "host_id", "license"],
    errors="ignore"
)

numeric_summary = (
    df[numeric_columns]
    .agg(["min", "max", "mean", "std"])
    .T
)

print("\nNumerical Summary Statistics:")
print(numeric_summary)

# Explicit price statistics
print("\nPrice Summary Statistics:")
print(
    df["price"]
    .agg(["count", "min", "max", "mean", "std"])
)
# Missing values
print("\nMissing Values Per Column:")
print(df.isna().sum())
# Categorical columns
categorical_columns = df.select_dtypes(
include=["object", "string"]
).columns
21
print("\nCategorical Value Counts:")
for column in categorical_columns:

    counts = df[column].value_counts(dropna=False)

    print(f"\n--- {column} ---")

    # Show all categories when there are relatively few
    if len(counts) <= 50:
        print(counts)

    # Avoid huge terminal output for columns such as
    # listing name, host name and review dates
    else:
        print(f"Number of unique categories: {df[column].nunique()}")
        print("Top 10 most common values:")
        print(counts.head(10))