"""
===============================================================================
STATS NZ AREA CODE ENRICHMENT
===============================================================================
Purpose:
    Enriches the Christchurch Airbnb dataset with Stats NZ SA2 area codes by 
    querying the Koordinates API using unique latitude/longitude pairs.

Inputs:
    - data/processed/christchurch_listings_2025_10_to_2026_06.csv
    - Environment Variable: KOORDINATES_API_KEY

Outputs:
    - Christchurch_coordinate_area_lookup.csv (Cached coordinate-to-SA2 mapping)
    - Christchurch_Airbnb_with_area_codes.csv (Enriched Airbnb dataset)
===============================================================================
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
# 3. API KEY VALIDATION
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

import os
from pathlib import Path

import pandas as pd

# Coordinates are rounded to 6 decimals (~10 cm) only when comparing with
# the cache, so tiny float differences don't make cached points look new.
COORD_DECIMALS = 6

# Never accepted as a real area code (counted as a failed lookup instead).
PLACEHOLDER_CODES = {"", "unknown", "n/a", "na", "none", "null", "nan"}

# False = any failed lookup stops the pipeline before it claims success.
ALLOW_PARTIAL_LOOKUP = False


def empty_lookup():
    """Empty lookup table with the right column types."""
    return pd.DataFrame({
        "latitude": pd.Series(dtype="float64"),
        "longitude": pd.Series(dtype="float64"),
        "area_code": pd.Series(dtype="object"),
    })


def is_missing_code(value):
    """True if an area code is missing or a placeholder like 'Unknown'."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    return str(value).strip().lower() in PLACEHOLDER_CODES


def query_one_safely(lat, lon):
    """
    Calls existing query function and turns any failure into a reason.
    Returns (area_code, None) on success or (None, reason) on failure.
    """
    api_key = os.environ.get("KOORDINATES_API_KEY", "")
    try:
        code = query_coordinate(lat, lon)  
    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"
        if api_key:
            reason = reason.replace(api_key, "***REDACTED***")  # never print the key
        return None, reason
    if is_missing_code(code):
        return None, f"No area code returned (got {code!r})"
    return str(code).strip(), None

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

    # --- Load existing lookup as a cache ---
    lookup_path = Path(LOOKUP_FILE)
    if lookup_path.exists():
        cached = pd.read_csv(lookup_path, dtype={"area_code": str})
        cached = cached[["latitude", "longitude", "area_code"]].copy()
        cached["latitude"] = pd.to_numeric(cached["latitude"], errors="coerce").round(COORD_DECIMALS)
        cached["longitude"] = pd.to_numeric(cached["longitude"], errors="coerce").round(COORD_DECIMALS)

        # Entries saved without a real code (e.g. 'Unknown') are re-queried
        bad = (
            cached["latitude"].isna()
            | cached["longitude"].isna()
            | cached["area_code"].apply(is_missing_code)
        )
        if bad.any():
            print(f"⚠️  {int(bad.sum())} cached entries have no valid area code; they will be re-queried.")
        cached = cached[~bad].drop_duplicates(["latitude", "longitude"]).reset_index(drop=True)
        print(f"🗂️  Loaded lookup cache: {len(cached)} known coordinate pairs.")
    else:
        cached = empty_lookup()
        print("🗂️  No lookup cache found; starting a new one.")

    known = set(zip(cached["latitude"], cached["longitude"]))

    # --- Unique coordinates in the current dataset ---
    coords = (
        combined[["latitude", "longitude"]]
        .apply(pd.to_numeric, errors="coerce")
        .dropna()
        .round(COORD_DECIMALS)
        .drop_duplicates()
    )

    # --- Only coordinates not already in the cache ---
    new_coords = [
        (lat, lon)
        for lat, lon in coords.itertuples(index=False, name=None)
        if (lat, lon) not in known
    ]

    print(
        f"📍 Unique coordinate pairs: {len(coords)} | "
        f"already cached: {len(coords) - len(new_coords)} | "
        f"new to query: {len(new_coords)}"
    )
    

    # ============================================================
    # QUERY KOORDINATES (sequential, no multiprocessing)
    # ============================================================

    results = []    # successful lookups this run
    failures = []   # failed lookups this run, with reasons
    total = len(new_coords)

    for i, (lat, lon) in enumerate(new_coords, start=1):
        try:
            code, reason = query_one_safely(lat, lon)
        except KeyboardInterrupt:
            print(f"\n⏹️  Interrupted after {i - 1}/{total} requests; saving what was found.")
            break

        if code is None:
            failures.append({"latitude": lat, "longitude": lon, "reason": reason})
            print(f"  ❌ ({lat}, {lon}) failed: {reason}")
        else:
            results.append({"latitude": lat, "longitude": lon, "area_code": code})

        if i % 100 == 0 or i == total:
            print(f"   ... {i}/{total} done ({len(failures)} failed)")

    # ========================================================
    # CREATE LOOKUP TABLE
    # ========================================================

    new_lookup = pd.DataFrame(results, columns=["latitude", "longitude", "area_code"])

    # Cached entries + new successes. Failed coordinates are NOT added,
    # so they get no invented value and are retried next run.
    frames = [f for f in (cached, new_lookup) if not f.empty]
    lookup = pd.concat(frames, ignore_index=True) if frames else empty_lookup()
    lookup = lookup.drop_duplicates(["latitude", "longitude"], keep="first").reset_index(drop=True)

    if len(lookup) != len(cached) + len(new_lookup):
        raise ValueError(
            f"Lookup size mismatch: {len(lookup)} rows, "
            f"expected {len(cached) + len(new_lookup)}."
        )

    

    # ========================================================
    # SAVE LOOKUP IMMEDIATELY
    # ========================================================

    # Save to a temp file first, then swap it in, so an interrupted
    # save can never corrupt the cache.
    lookup_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = lookup_path.with_name(lookup_path.name + ".tmp")
    lookup.to_csv(tmp_path, index=False)
    os.replace(tmp_path, lookup_path)
    print(
        f"💾 Lookup saved: {len(lookup)} pairs "
        f"({len(new_lookup)} added this run) -> {lookup_path}"
    )

    # ========================================================
    # CHECK QUERY RESULTS
    # ========================================================

    print("\n" + "=" * 50)
    print("🔎 QUERY RESULTS")
    print("=" * 50)
    print(f"Coordinates reused from cache:  {len(coords) - len(new_coords)}")
    print(f"New coordinates queried:        {len(new_coords)}")
    print(f"  Successful:                   {len(results)}")
    print(f"  Failed:                       {len(failures)}")
    if new_coords:
        print(f"  Success rate (this run):      {len(results) / len(new_coords) * 100:.2f}%")
    print("=" * 50)

    if failures:
        print("⚠️  Failed coordinates (not cached, will be retried next run):")
        for f in failures[:20]:
            print(f"  - ({f['latitude']}, {f['longitude']}): {f['reason']}")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more (see log above)")

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

    merged = combined.copy()
    if "area_code" in merged.columns:
        merged = merged.drop(columns=["area_code"])  # replaced with the full lookup

    # Match on rounded keys; the real latitude/longitude values are untouched
    merged["_lat_key"] = pd.to_numeric(merged["latitude"], errors="coerce").round(COORD_DECIMALS)
    merged["_lon_key"] = pd.to_numeric(merged["longitude"], errors="coerce").round(COORD_DECIMALS)

    merged = merged.merge(
        lookup.rename(columns={"latitude": "_lat_key", "longitude": "_lon_key"}),
        on=["_lat_key", "_lon_key"],
        how="left",
        validate="many_to_one",  # stops if the lookup has duplicate coordinates
    ).drop(columns=["_lat_key", "_lon_key"])

    if len(merged) != len(combined):
        raise ValueError(f"Row count changed during merge: {len(combined)} -> {len(merged)}.")


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
    has_coords = merged["latitude"].notna() & merged["longitude"].notna()
    unresolved = int((has_coords & merged["area_code"].isna()).sum())

    if failures or unresolved:
        problem = (
            f"Area-code lookup is INCOMPLETE: {unresolved} row(s) with coordinates "
            f"have no area code; {len(failures)} coordinate pair(s) failed this run. "
            f"Successful results are cached; rerun to retry only the failed ones."
        )
        if not ALLOW_PARTIAL_LOOKUP:
            raise RuntimeError(problem)
        print("⚠️  WARNING: " + problem)

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

def validate_spatial_data(df: pd.DataFrame, lookup_df: pd.DataFrame) -> None:
    """
    Sanity checks for coordinate bounds and merge integrity in area_code.py.
    """
    # Check 1: Geographically valid boundaries for Christchurch
    LAT_BOUNDS = (-44.2, -43.2)
    LON_BOUNDS = (171.8, 173.5)
    
    invalid_coords = df[
        ~df["latitude"].between(*LAT_BOUNDS) | 
        ~df["longitude"].between(*LON_BOUNDS)
    ]
    if not invalid_coords.empty:
        print(f"⚠️ SANITY WARNING: Found {len(invalid_coords)} rows with coordinates outside Canterbury region.")

    # Check 2: API hit-rate threshold check
    success_rate = lookup_df["area_code"].notna().mean() * 100
    print(f"🔍 SANITY CHECK: Spatial Lookup Match Rate = {success_rate:.2f}%")
    assert success_rate > 50.0, f"Critical Failure: Match rate ({success_rate:.2f}%) below 50% threshold!"

    # Check 3: Merge Row Count Integrity (Input Rows == Output Rows)
    assert len(df) == len(lookup_df), "Merge Error: Output dataset row count does not match input!"