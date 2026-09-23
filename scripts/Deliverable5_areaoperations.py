import pandas as pd
import numpy as np

# Import packages
# (pandas + numpy cover dplyr-equivalent functionality)

# Read in the csvs
bnb = pd.read_csv("Christchurch_Airbnb_with_area_codes.csv")
tenancy = pd.read_csv("data/raw/tenancy_final.csv")

# Convert into uniform time format
time_map = {
    "Oct-25": "1/10/2025", "Nov-25": "1/10/2025", "Dec-25": "1/10/2025",
    "Jan-26": "1/01/2026", "Feb-26": "1/01/2026", "Mar-26": "1/01/2026",
    "Apr-26": "1/04/2026", "May-26": "1/04/2026", "Jun-26": "1/04/2026",
}
bnb2 = bnb.copy()
bnb2["TimeFrame"] = bnb2["month_year"].map(time_map)
print(bnb2.columns.tolist())

# Make a new dataset of all unique combinations of Time + Location ID,
# add weekly rent, then convert to nightly rent to match the Airbnb dataset
tenancy2 = tenancy[
    tenancy["Location.Id"].notna() & (tenancy["Location.Id"] != -99)
]

tenancy2 = (
    tenancy2.groupby(["Location.Id", "TimeFrame"], as_index=False)
    .agg(
        Weekly_Rent=("Median.Rent", "mean"),
        Active_Bonds=("Active.Bonds", "sum"),
    )
)

tenancy2["Daily_Rent"] = tenancy2["Weekly_Rent"] / 7

# Inner join the datasets based on time and location
combined = bnb2.merge(
    tenancy2,
    left_on=["area_code", "TimeFrame"],
    right_on=["Location.Id", "TimeFrame"],
    how="inner",
)

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
        Gap=("Rent_Gap", "median"),
        Crazy_Gap=("Rent_Gap", "max"),
    )
    .sort_values("Gap", ascending=False)
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