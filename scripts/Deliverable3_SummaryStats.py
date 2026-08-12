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
print("\nNumerical Summary Statistics:")
print(df.describe())
# Missing values
print("\nMissing Values Per Column:")
print(df.isna().sum())
# Categorical columns
categorical_columns = df.select_dtypes(
include=["object"]
).columns
21
print("\nCategorical Value Counts:")
for column in categorical_columns:
    print(f"\n--- {column} ---")
    print(df[column].value_counts(dropna=False))