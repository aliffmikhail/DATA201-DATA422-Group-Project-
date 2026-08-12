import os
import pandas as pd

# Define paths
processed_folder = "data/processed"
output_file = os.path.join(processed_folder, "christchurch_listings_2025_10_to_2026_06.csv")

# List all 9 processed Christchurch files
files = [
    "christchurch_2025_10.csv",
    "christchurch_2025_11.csv",
    "christchurch_2025_12.csv",
    "christchurch_2026_01.csv",
    "christchurch_2026_02.csv",
    "christchurch_2026_03.csv",
    "christchurch_2026_04.csv",
    "christchurch_2026_05.csv",
    "christchurch_2026_06.csv",
]

# Read and load each dataset
dataframes = []
for file_name in files:
    file_path = os.path.join(processed_folder, file_name)
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Concatenate all dataframes into one
combined_df = pd.concat(dataframes, ignore_index=True)

# Save the combined dataset
combined_df.to_csv(output_file, index=False)