"""
DATA422 - Add Stats NZ area codes to Christchurch Airbnb data

Input:
    data/processed/christchurch_listings_2025_10_to_2026_06.csv

Outputs:
    Christchurch_coordinate_area_lookup.csv
    Christchurch_Airbnb_with_area_codes.csv

Process:
    1. Load cleaned Airbnb dataset
    2. Extract unique latitude/longitude pairs
    3. Query Koordinates for each unique coordinate
    4. Extract Stats NZ SA2 area code
    5. Save coordinate lookup
    6. Merge area codes back into Airbnb dataset
    7. Save final dataset
"""

import os
import time

import pandas as pd
import requests


# ============================================================
# 1. FILE SETTINGS
# ============================================================

INPUT_FILE = "data/processed/christchurch_listings_2025_10_to_2026_06.csv"

LOOKUP_FILE = "Christchurch_coordinate_area_lookup.csv"

OUTPUT_FILE = "Christchurch_Airbnb_with_area_codes.csv"


# ============================================================
# 2. KOORDINATES SETTINGS
# ============================================================

API_URL = (
    "https://koordinates.com/services/query/v1/vector.json"
)

# Confirmed from the successful test query
LAYER_ID = 123515

# Confirmed from the successful test query
AREA_CODE_FIELD = "SA22026_V1_00"


# ============================================================
# 3. API KEY
# ============================================================

API_KEY = os.environ.get(
    "KOORDINATES_API_KEY"
)

if not API_KEY:

    raise RuntimeError(
        "\nKOORDINATES_API_KEY is not set.\n\n"
        "Run this first in your terminal:\n\n"
        '$env:KOORDINATES_API_KEY="YOUR_NEW_API_KEY"\n'
    )


# ============================================================
# 4. FUNCTION TO QUERY ONE COORDINATE
# ============================================================

def query_coordinate(coordinate):

    """
    Send one latitude/longitude pair to Koordinates
    and return the corresponding Stats NZ area code.
    """

    latitude, longitude = coordinate

    params = {

        "key": API_KEY,

        "layer": LAYER_ID,

        # Koordinates expects:
        # x = longitude
        # y = latitude

        "x": longitude,
        "y": latitude,

        "max_results": 1,

        "radius": 0,

        "geometry": "false",

        "with_field_names": "true"
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=(5, 10)   # (connect timeout, read timeout) - both short
        )

        response.raise_for_status()

        result = response.json()

        # ====================================================
        # Extract layers
        # ====================================================

        vector_query = result.get(
            "vectorQuery",
            {}
        )

        layers = vector_query.get(
            "layers",
            {}
        )

        # Layer keys are returned as strings
        layer = layers.get(
            str(LAYER_ID),
            {}
        )

        features = layer.get(
            "features",
            []
        )

        # ====================================================
        # No feature found
        # ====================================================

        if not features:

            return (
                latitude,
                longitude,
                None
            )

        # ====================================================
        # Extract area code
        # ====================================================

        properties = features[0].get(
            "properties",
            {}
        )

        area_code = properties.get(
            AREA_CODE_FIELD
        )

        return (
            latitude,
            longitude,
            area_code
        )

    except Exception as error:

        print(
            f"\nERROR"
            f"\nLatitude: {latitude}"
            f"\nLongitude: {longitude}"
            f"\n{error}"
        )

        return (
            latitude,
            longitude,
            None
        )


# ============================================================
# 5. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "DATA422 - ADDING STATS NZ AREA CODES"
    )

    print("=" * 70)

    # ========================================================
    # LOAD DATA
    # ========================================================

    data = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"\nLoaded Airbnb dataset:"
        f" {data.shape[0]:,} rows x "
        f"{data.shape[1]} columns"
    )

    # ========================================================
    # CHECK REQUIRED COLUMNS
    # ========================================================

    required_columns = {
        "id",
        "latitude",
        "longitude",
        "month_year"
    }

    missing_columns = (
        required_columns
        - set(data.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    print(
        "\nRequired columns are present."
    )

    # ========================================================
    # GET UNIQUE COORDINATES
    # ========================================================

    coordinates = (
        data[
            [
                "latitude",
                "longitude"
            ]
        ]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    coordinate_list = list(
        coordinates.itertuples(
            index=False,
            name=None
        )
    )

    print(
        f"\nTotal Airbnb rows:"
        f" {len(data):,}"
    )

    print(
        f"Unique coordinates to query:"
        f" {len(coordinate_list):,}"
    )

    # ============================================================
    # QUERY KOORDINATES (sequential, no multiprocessing)
    # ============================================================

    print("\nStarting Koordinates queries...")

    start_time = time.time()

    results = []

    for i, coordinate in enumerate(coordinate_list):

        print(f"Querying {i + 1}/{len(coordinate_list)}: {coordinate}", flush=True)

        results.append(query_coordinate(coordinate))

        if (i + 1) % 200 == 0:
            print(f"Queried {i + 1:,} / {len(coordinate_list):,}")

    elapsed_time = time.time() - start_time

    print(f"\nQueries completed in: {elapsed_time:.1f} seconds")

    # ========================================================
    # CREATE LOOKUP TABLE
    # ========================================================

    lookup = pd.DataFrame(
        results,
        columns=[
            "latitude",
            "longitude",
            "area_code"
        ]
    )

    # ========================================================
    # SAVE LOOKUP IMMEDIATELY
    # ========================================================

    lookup.to_csv(
        LOOKUP_FILE,
        index=False
    )

    print(
        f"\nSaved coordinate lookup:"
        f" {LOOKUP_FILE}"
    )

    # ========================================================
    # CHECK QUERY RESULTS
    # ========================================================

    successful = (
        lookup["area_code"]
        .notna()
        .sum()
    )

    failed = (
        lookup["area_code"]
        .isna()
        .sum()
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "QUERY RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nUnique coordinates:"
        f" {len(lookup):,}"
    )

    print(
        f"Area codes found:"
        f" {successful:,}"
    )

    print(
        f"Area codes missing:"
        f" {failed:,}"
    )

    # ========================================================
    # SHOW SAMPLE RESULTS
    # ========================================================

    print(
        "\nSample area-code results:"
    )

    print(
        lookup.head(10).to_string(
            index=False
        )
    )

    # ========================================================
    # MERGE AREA CODES INTO AIRBNB DATA
    # ========================================================

    data = data.merge(

        lookup[
            [
                "latitude",
                "longitude",
                "area_code"
            ]
        ],

        on=[
            "latitude",
            "longitude"
        ],

        how="left"
    )

    # ========================================================
    # CHECK FINAL DATASET
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL AIRBNB DATASET"
    )

    print(
        "=" * 70
    )

    print(
        f"\nFinal rows:"
        f" {len(data):,}"
    )

    print(
        f"Final columns:"
        f" {len(data.columns)}"
    )

    print(
        f"\nRows with area code:"
        f" {data['area_code'].notna().sum():,}"
    )

    print(
        f"Rows without area code:"
        f" {data['area_code'].isna().sum():,}"
    )

    # ========================================================
    # SAVE FINAL DATASET
    # ========================================================

    data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved final dataset:"
        f" {OUTPUT_FILE}"
    )

    # ========================================================
    # FINAL CHECK
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "POINTS 1-4 COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        "\nYour Airbnb dataset now contains:"
    )

    print(
        "latitude + longitude + Stats NZ area_code"
    )

    print(
        "\nThe dataset is ready for the next team's"
    )

    print(
        "area-code/time join."
    )