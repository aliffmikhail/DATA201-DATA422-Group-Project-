import pandas as pd
from pathlib import Path

# ==========================================
# 1. LOAD DATA
# ==========================================

df = pd.read_csv("data/raw/rental_bond_detailed_2020_2026.csv")

print("Original dataset:", df.shape)

df["TimeFrame"] = pd.to_datetime(df["TimeFrame"], errors="coerce")

if df["TimeFrame"].isna().any():
    raise ValueError("Invalid or missing TimeFrame values found.")


# ==========================================
# 2. FILTER TIMEFRAME
# ==========================================

bond = df[
    (df["TimeFrame"] >= "2025-10-01") &
    (df["TimeFrame"] < "2026-07-01")
].copy()

print("\n========== TIMEFRAME ==========")
print("Rows before:", len(df))
print("Rows after:", len(bond))
print("Rows excluded:", len(df) - len(bond))

print("\nRetained reporting dates:")
print(bond["TimeFrame"].value_counts().sort_index())


# ==========================================
# 3. INVESTIGATE DATA QUALITY
# ==========================================

print("\n========== MISSING VALUES ==========")
print(bond.isna().sum())

# Check missing values and special IDs by reporting date
checks = pd.DataFrame({
    "TimeFrame": bond["TimeFrame"],
    "Missing Location": bond["Location Id"].isna(),
    "Missing Beds": bond["Number Of Beds"].isna(),
    "Missing Rent": bond["Median Rent"].isna(),
    "Location -99": bond["Location Id"] == -99
})

print("\nIssues by reporting date:")
print(checks.groupby("TimeFrame").sum().to_string())

# Confirm the overlap between missing locations and rents
missing_location = bond["Location Id"].isna()
missing_rent = bond["Median Rent"].isna()

print("\nRows missing both location and median rent:")
print((missing_location & missing_rent).sum())

print("Exactly the same missing rows?")
print(missing_location.equals(missing_rent))

# Investigate missing bedroom information
print("\nMissing bedrooms by dwelling type:")
print(
    bond.loc[
        bond["Number Of Beds"].isna(),
        "Dwelling Type"
    ].value_counts(dropna=False)
)

# Explicit ALL categories
print("\nALL category counts:")
print("Dwelling Type:", (bond["Dwelling Type"] == "ALL").sum())
print("Number Of Beds:", (bond["Number Of Beds"] == "ALL").sum())

# Special geographic identifier
print("\nLocation -99:", (bond["Location Id"] == -99).sum())


# ==========================================
# 4. NUMERICAL VALIDATION
# ==========================================

print("\n========== VALIDATION ==========")

bond_columns = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds"
]

rent_columns = [
    "Median Rent",
    "Geometric Mean Rent",
    "Lower Quartile Rent",
    "Upper Quartile Rent"
]

negative_bonds = (bond[bond_columns] < 0).sum()
invalid_rents = (bond[rent_columns] <= 0).sum()

invalid_quartiles = (
    (bond["Lower Quartile Rent"] > bond["Median Rent"]) |
    (bond["Median Rent"] > bond["Upper Quartile Rent"])
).sum()

duplicates = bond.duplicated().sum()

print("\nNegative bond counts:")
print(negative_bonds)

print("\nNon-positive rents:")
print(invalid_rents)

print("\nInvalid quartile ordering:", invalid_quartiles)
print("Exact duplicate rows:", duplicates)

if (
    negative_bonds.sum() > 0 or
    invalid_rents.sum() > 0 or
    invalid_quartiles > 0 or
    duplicates > 0
):
    raise ValueError("Validation failed. Review the data.")


# ==========================================
# 5. REMOVE MISSING LOCATION IDs
# ==========================================

print("\n========== CLEANING ==========")

# Missing locations cannot support geographic matching.
# These records also have missing median rents.
# Other missing values and special categories are preserved.

cleaned = bond.dropna(subset=["Location Id"]).copy()

print("Rows before:", len(bond))
print("Rows removed:", len(bond) - len(cleaned))
print("Rows remaining:", len(cleaned))

print("\nRemaining missing values:")
print(cleaned.isna().sum())


# ==========================================
# 6. SAVE AND VERIFY
# ==========================================

output = Path(
    "data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv"
)

output.parent.mkdir(parents=True, exist_ok=True)

cleaned.to_csv(
    output,
    index=False,
    date_format="%Y-%m-%d"
)

# Verify the exported CSV
saved = pd.read_csv(output)

assert saved.shape == cleaned.shape
assert saved.columns.tolist() == cleaned.columns.tolist()
assert saved["Location Id"].notna().all()

print("\n========== FINAL OUTPUT ==========")
print("Saved to:", output)
print("Final shape:", saved.shape)
print("Export verification passed.")