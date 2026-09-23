import pandas as pd
import numpy as np

# Import packages
# (pandas + numpy cover dplyr-equivalent functionality)

# Load final cleaned Airbnb data
bnb = pd.read_csv(
    "data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv"
)

# Reuse the area codes that were already queried from Koordinates
mapped_bnb = pd.read_csv("Christchurch_Airbnb_with_area_codes.csv")

area_codes = (
    mapped_bnb[["id", "month_year", "area_code"]]
    .drop_duplicates(["id", "month_year"])
)

bnb = bnb.merge(
    area_codes,
    on=["id", "month_year"],
    how="left",
    validate="many_to_one"
)

# Load final cleaned bond data from Deliverable 4
tenancy = pd.read_csv(
    "data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv"
)

# Keep the existing D5 naming style
tenancy = tenancy.rename(columns={
    "Location Id": "Location.Id",
    "Dwelling Type": "Dwelling.Type",
    "Number Of Beds": "Number.Of.Beds",
    "Median Rent": "Median.Rent",
    "Active Bonds": "Active.Bonds"
})

time_map = {
    "2025-10": "2025-10-01",
    "2025-11": "2025-10-01",
    "2025-12": "2025-10-01",

    "2026-01": "2026-01-01",
    "2026-02": "2026-01-01",
    "2026-03": "2026-01-01",

    "2026-04": "2026-04-01",
    "2026-05": "2026-04-01",
    "2026-06": "2026-04-01"
}

bnb2 = bnb.copy()
bnb2["TimeFrame"] = bnb2["month_year"].map(time_map)

print("\nMissing TimeFrames:", bnb2["TimeFrame"].isna().sum())

# Use the existing overall location-level bond record
tenancy2 = tenancy[
    (tenancy["Dwelling.Type"] == "ALL") &
    (tenancy["Number.Of.Beds"] == "ALL")
].copy()

# Make dates and location IDs compatible with Airbnb
tenancy2["TimeFrame"] = (
    pd.to_datetime(tenancy2["TimeFrame"])
    .dt.strftime("%Y-%m-%d")
)

bnb2["area_code"] = pd.to_numeric(
    bnb2["area_code"],
    errors="coerce"
).astype("Int64")

tenancy2["Location.Id"] = pd.to_numeric(
    tenancy2["Location.Id"],
    errors="coerce"
).astype("Int64")

# Rename only the columns already used later in the script
tenancy2 = tenancy2.rename(columns={
    "Median.Rent": "Weekly_Rent",
    "Active.Bonds": "Active_Bonds"
})

print(
    "\nDuplicate tenancy location-time keys:",
    tenancy2.duplicated(["Location.Id", "TimeFrame"]).sum()
)

# Convert weekly long-term rent to nightly equivalent
tenancy2["Daily_Rent"] = tenancy2["Weekly_Rent"] / 7

combined = bnb2.merge(
    tenancy2,
    left_on=["area_code", "TimeFrame"],
    right_on=["Location.Id", "TimeFrame"],
    how="left",
    validate="many_to_one",
    indicator=True
)

print("\nAirbnb rows before join:", len(bnb2))
print("Rows after join:", len(combined))

print("\nJoin results:")
print(combined["_merge"].value_counts())

matched_percent = (
    (combined["_merge"] == "both").mean() * 100
)

print(f"\nMatched Airbnb rows: {matched_percent:.1f}%")

# Keep only matched rows for the rent-gap analysis
combined = combined[
    combined["_merge"] == "both"
].copy()

# Median AirBnB price in CHC Central
median_price_chc_central = (
    bnb.loc[bnb["area_code"] == 326600, "price"]
    .median()
)
print(f"Median Airbnb Price: {median_price_chc_central}")

# Finding the largest gap between long- and short-term rent
combined["Rent_Gap"] = combined["price"] - combined["Daily_Rent"]

gaps = (
    combined.groupby("area_code", as_index=False)
    .agg(
        Median_Gap=("Rent_Gap", "median"),
        Maximum_Gap=("Rent_Gap", "max"),
        Observations=("Rent_Gap", "count"),
    )
    .sort_values("Median_Gap", ascending=False)
)

# Comparing the number of AirBnB and rental properties in each area
airbnb_counts = (
    bnb2.groupby(["area_code", "TimeFrame"], as_index=False)
    .agg(Airbnb_Count=("id", "nunique"))
)

tenancy_counts = tenancy2[["Location.Id", "TimeFrame", "Active_Bonds"]]

property_counts = airbnb_counts.merge(
    tenancy_counts,
    left_on=["area_code", "TimeFrame"],
    right_on=["Location.Id", "TimeFrame"],
    how="inner",
)

# ============================================================
# PRINT RESULTS
# ============================================================
 
print("\nTop 10 areas by rent gap:")
print(gaps.head(10).to_string(index=False))
 
print("\nProperty counts sample:")
print(property_counts.head(10).to_string(index=False))

largest_typical = gaps.iloc[0]

largest_single = gaps.loc[
    gaps["Maximum_Gap"].idxmax()
]

print("\nArea with largest median rent gap:")
print(largest_typical.to_string())

print("\nArea with largest single rent gap:")
print(largest_single.to_string())