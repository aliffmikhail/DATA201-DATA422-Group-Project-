# Deliverable 6 - Pipeline Design Principles

## AI Use

ChatGPT by OpenAI was used to assist with drafting and organising this design-principles document.

The final content was reviewed against the project code, datasets, and intended pipeline before being included in the project documentation.

---

## Purpose

The purpose of this pipeline is to transform raw Christchurch Airbnb data and New Zealand rental bond data into cleaned and geographically aligned datasets that can be used to compare short-term and long-term rental patterns.

The pipeline is designed to be:

- reproducible,
- understandable by different team members,
- easy to validate,
- and organised into clear processing stages.

---

## Pipeline Overview

The overall pipeline is:

Raw Airbnb data  
→ Combine monthly Airbnb files  
→ Clean Airbnb data  
→ Map latitude/longitude to SA2 area codes  
→ Align with cleaned rental bond data  
→ Match time periods  
→ Join by area and time  
→ Analyse rental prices and counts  
→ Produce final outputs

The rental bond side of the pipeline is:

Raw rental bond data  
→ Filter to the required study period  
→ Clean and validate the data  
→ Save processed rental bond data  
→ Use as an input for the integration stage

Each stage produces an output that can be used by the next stage.

---

## Pipeline Inputs

### Airbnb Data

The pipeline uses monthly Christchurch Airbnb listing data sourced from Inside Airbnb.

Important fields used in later stages include:

- `id`
- `latitude`
- `longitude`
- `price`
- `month_year`
- `room_type`
- review and availability information

After cleaning, the Airbnb dataset contains 18,080 listing-month observations covering October 2025 to June 2026.

The cleaned Airbnb data are used as the short-term rental input for the integration stage.

### Rental Bond Data

The long-term rental input is the Tenancy Services detailed quarterly rental bond dataset.

Important fields include:

- `TimeFrame`
- `Location Id`
- `Dwelling Type`
- `Number Of Beds`
- `Active Bonds`
- `Median Rent`
- rental quartile information

After cleaning, the rental bond dataset contains 26,991 rows and 12 columns.

The cleaned bond data provide long-term rental benchmarks by location and reporting period.

### Geographic Mapping

Airbnb listings contain latitude and longitude coordinates but do not contain the geographic `Location Id` used by the rental bond dataset.

`scripts/area_code.py` uses the Koordinates API to obtain a Stats NZ SA2 area code from Airbnb coordinates.

The mapping results are saved so they can be reused without repeating the API requests.

Saved mapping files include:

- `Christchurch_coordinate_area_lookup.csv`
- `Christchurch_Airbnb_with_area_codes.csv`

---

## Pipeline Outputs

### Cleaned Airbnb Data

`data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv`

This contains the cleaned Airbnb observations used for later analysis.

### Cleaned Rental Bond Data

`data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv`

This contains the cleaned rental bond observations used in the integration stage.

### Saved Area-Code Lookup

`Christchurch_coordinate_area_lookup.csv`

This stores the relationship between Airbnb coordinates and Stats NZ area codes.

### Airbnb Data with Area Codes

`Christchurch_Airbnb_with_area_codes.csv`

This preserves the geographic mapping produced by the Koordinates API.

The saved area codes can then be reused with the final cleaned Airbnb dataset.

### Integrated Analysis Outputs

The integration stage produces information including:

- matched Airbnb and rental bond observations,
- Christchurch Central median Airbnb price,
- median short-term versus long-term rental price gaps,
- maximum observed price gaps,
- observation counts by area,
- Airbnb listing counts,
- active rental bond counts.

---

## Main Pipeline Steps

### Step 1 - Combine Airbnb Files

Monthly Airbnb listing files are loaded and combined into a single Christchurch dataset.

A `month_year` field is retained so each observation can later be aligned with the rental bond reporting periods.

### Step 2 - Clean Airbnb Data

The Airbnb data are cleaned before being used in later stages.

Cleaning includes handling:

- missing prices,
- unsuitable price records,
- missing values,
- unnecessary or uninformative columns.

The final cleaned Airbnb dataset contains 18,080 listing-month observations.

### Step 3 - Clean Rental Bond Data

The rental bond dataset is filtered to the required study period and checked for:

- missing location identifiers,
- special location codes,
- missing rental values,
- duplicate records,
- invalid bond counts,
- invalid rental values,
- inconsistent rental quartiles.

The final cleaned rental bond dataset contains 26,991 rows.

### Step 4 - Map Airbnb Coordinates to Geographic Areas

`scripts/area_code.py` extracts unique latitude and longitude combinations and queries the Koordinates API for Stats NZ SA2 area codes.

The coordinate-to-area-code mapping is saved for reuse.

This creates the geographic key needed to connect Airbnb records with rental bond records.

### Step 5 - Attach Area Codes to the Cleaned Airbnb Data

The saved area-code results are transferred onto the final cleaned Airbnb dataset.

The mapping is matched using:

- `id`
- `month_year`

This allows the existing geographic mapping to be reused without rerunning the Koordinates API.

### Step 6 - Align the Datasets in Time

Airbnb observations are monthly, while the rental bond data use quarterly reporting reference dates.

The Airbnb observations are aligned as follows:

| Airbnb Months | Bond TimeFrame |
| --- | --- |
| Oct-Dec 2025 | 2025-10-01 |
| Jan-Mar 2026 | 2026-01-01 |
| Apr-Jun 2026 | 2026-04-01 |

This creates a common time field for the integration stage.

### Step 7 - Prepare the Rental Bond Benchmark

The rental bond dataset contains multiple dwelling and bedroom categories for the same location and reporting period.

For the general location-level comparison, the pipeline selects records where:

- `Dwelling Type = ALL`
- `Number Of Beds = ALL`

This provides one overall bond record for each location and reporting period.

Weekly median rent is converted to a daily equivalent:

`Daily Rent = Median Rent / 7`

This allows the long-term rental value to be compared with Airbnb nightly prices.

### Step 8 - Join Airbnb and Rental Bond Data

The datasets are joined using:

- Airbnb `area_code` and bond `Location Id`
- `TimeFrame`

The join initially keeps unmatched Airbnb observations visible so the integration can be checked.

This allows the pipeline to inspect:

- matched observations,
- unmatched observations,
- duplicate join behaviour,
- row counts before and after the merge.

Only successfully matched observations are then used for the rental-price comparison.

### Step 9 - Produce Analysis Results

The integrated data are used to calculate:

- median Airbnb price in Christchurch Central,
- short-term versus long-term rental price gaps,
- median price gap by area,
- maximum observed price gap by area,
- number of observations supporting each area result,
- unique Airbnb listing counts,
- active rental bond counts.

---

## Coding and Software Design Principles

The following coding practices were selected because they directly apply to this project.

### Clear Interfaces Between Pipeline Stages

Each major stage should produce a clearly defined output that becomes an input for the next stage.

For example:

Raw rental bond data  
→ Rental bond cleaning  
→ Cleaned rental bond dataset  
→ Deliverable 5 integration

Similarly:

Airbnb coordinates  
→ Koordinates mapping  
→ Saved area-code lookup  
→ Cleaned Airbnb data with area codes

This makes the pipeline easier to understand and reproduce.

It also reduces reliance on unexplained intermediate files.

### Self-Documenting Code

Variable names and output names should describe what they contain.

Examples include:

- `Median_Gap`
- `Maximum_Gap`
- `Observations`
- `matched_percent`
- `Daily_Rent`

These names make the code easier to understand without requiring another team member to inspect every calculation.

Comments should mainly explain why an operation is required rather than simply repeat what the code already shows.

### Sanity Checking

Important pipeline stages should be checked against expected behaviour.

Examples include:

- checking missing values,
- checking duplicate records,
- checking negative bond counts,
- checking rental quartile ordering,
- checking missing `TimeFrame` values,
- checking duplicate location-time join keys,
- comparing row counts before and after joins,
- checking matched and unmatched observations.

Sanity checks help identify errors even when the code itself runs successfully.

For example, a merge may run without producing an error but still accidentally multiply the number of observations.

### Organised Files and Reusable Outputs

The project separates different types of files where possible, including:

- `data/raw/`
- `data/processed/`
- `scripts/`
- `outputs/`
- documentation files

Processed datasets use descriptive filenames so later pipeline stages can identify the correct inputs.

Slow or external operations should also save reusable outputs.

For example, the Koordinates API results are saved as a coordinate-to-area-code lookup.

This allows the mapping to be reused instead of repeating thousands of external API requests.

---

## Pipeline Limitations

### Geographic Definitions

The Airbnb geographic mapping currently uses a Stats NZ SA2 2026 field.

The rental bond source documentation refers to SA2-2019 geographic definitions.

Differences between these geographic definitions may contribute to Airbnb observations that do not match rental bond records.

### Different Time Resolutions

Airbnb observations are monthly, while rental bond observations use quarterly reporting reference dates.

Monthly Airbnb data therefore need to be aligned with the available bond reporting periods.

This reduces the temporal resolution of the combined analysis.

### Different Rental Markets

Airbnb prices represent advertised nightly short-term accommodation prices.

Rental bond median rents represent weekly long-term rental prices.

Weekly rent is divided by seven to provide a daily comparison unit, but this does not make the two rental markets directly equivalent.

The resulting price gap should therefore be interpreted as a comparison between short-term and long-term rental price measures rather than a direct profit measure.

---