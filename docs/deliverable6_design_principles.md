# Deliverable 6 - Pipeline Design Principles

## AI Use

ChatGPT by OpenAI was used to assist with drafting and organising this design-principles document.

The final content was reviewed against the project code, datasets, and intended pipeline before being included in the project documentation.

---

## Pipeline Purpose

The project pipeline transforms raw Christchurch Airbnb data and New Zealand rental bond data into cleaned and geographically aligned datasets for comparing short-term and long-term rental patterns.

At a high level:

Raw data → Cleaning → Geographic mapping → Time alignment → Join → Analysis

---

## Inputs

The main pipeline inputs are:

- Monthly Christchurch Airbnb listing CSV files from Inside Airbnb.
- Tenancy Services detailed quarterly rental bond data.
- Airbnb latitude and longitude coordinates used with the Koordinates API to obtain Stats NZ SA2 area codes.

The final cleaned datasets used by the integration stage are:

- `data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv`
- `data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv`

---

## Outputs

Important pipeline outputs include:

- cleaned Airbnb data,
- cleaned rental bond data,
- saved coordinate-to-area-code lookup,
- Airbnb observations with area codes,
- joined Airbnb/rental-bond observations,
- rental price-gap results,
- Airbnb listing and active-bond counts.

The saved geographic mapping allows the Koordinates API results to be reused rather than queried again.

---

## Main Pipeline Steps

1. Combine monthly Airbnb files and retain the observation month.
2. Clean the Airbnb data.
3. Clean and filter the rental bond data.
4. Use `area_code.py` to map Airbnb coordinates to Stats NZ SA2 area codes.
5. Reuse the saved area-code mapping with the cleaned Airbnb dataset.
6. Align monthly Airbnb observations with the available rental-bond reporting periods.
7. Select the overall `ALL` dwelling / `ALL` bedroom bond record for each location and period.
8. Convert weekly median rent to a daily equivalent.
9. Join Airbnb and rental-bond data by geographic area and `TimeFrame`.
10. Produce the final price-gap and rental-count analyses.

---

## Coding and Software Design Principles

### Clear Pipeline Interfaces

Each major stage produces a clearly defined output for the next stage.

For example:

Cleaned rental bond data → Deliverable 5 integration

and:

Koordinates mapping → saved area-code lookup → cleaned Airbnb integration

This makes the workflow easier to understand and reproduce.

### Self-Documenting Code

Descriptive names are used where possible, including:

- `Median_Gap`
- `Maximum_Gap`
- `Observations`
- `matched_percent`
- `Daily_Rent`

Comments are mainly used to explain why an operation is required rather than repeating what the code already shows.

### Sanity Checking

Important transformations are checked against expected behaviour.

Examples include:

- checking missing values,
- checking duplicate keys,
- validating geographic coordinates,
- comparing row counts before and after joins,
- recording matched and unmatched observations.

These checks help detect pipeline errors even when the code runs successfully.

### Organised Files and Reusable Outputs

Raw data, processed data, scripts, outputs, and documentation are kept separate where possible.

External or expensive operations also save reusable results. For example, the Koordinates area-code lookup is stored so that thousands of API queries do not need to be repeated.

---
