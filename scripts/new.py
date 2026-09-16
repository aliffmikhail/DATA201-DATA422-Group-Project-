import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load combined dataset
file_path = "data/processed/christchurch_listings_2025_10_to_2026_06.csv"
df = pd.read_csv(file_path)

# 2. Calculate missing values per column by month
monthly_missing = df.groupby("month_year").apply(lambda x: x.isna().sum())

# Drop the 'month_year' column count if present, and filter only columns with missing values
monthly_missing = monthly_missing.drop(columns=["month_year"], errors="ignore")
monthly_missing = monthly_missing.loc[:, (monthly_missing > 0).any()]

print("Monthly Missing Values Summary:")
print(monthly_missing)

# 3. Create line plot for missing values over time
plt.figure(figsize=(10, 6))
for col in monthly_missing.columns:
    plt.plot(monthly_missing.index, monthly_missing[col], marker='o', label=col)

plt.title("Missing Values per Column by Month (Christchurch)")
plt.xlabel("Month")
plt.ylabel("Count of Missing Values")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Save plot to outputs directory
os.makedirs("outputs", exist_ok=True)
plt.savefig("outputs/missing_values_by_month.png")
plt.show()

# 4. Optional: Heatmap visualization (Columns vs Months)
plt.figure(figsize=(10, 6))
sns.heatmap(monthly_missing.T, annot=True, fmt="d", cmap="YlOrRd", cbar_kws={'label': 'Missing Count'})
plt.title("Heatmap of Missing Values by Month")
plt.xlabel("Month")
plt.ylabel("Columns")
plt.tight_layout()
plt.savefig("outputs/missing_values_heatmap.png")
plt.show()