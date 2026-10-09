# Deliverable 7 - Airbnb Pipeline Automation

## Purpose

Deliverable 7 extends the existing Airbnb workflow so that newly available monthly datasets can be incorporated without manually editing month lists or running each processing script individually.

The final workflow is orchestrated through:

```bash
python scripts/run_airbnb_pipeline.py
```

The objective is to reuse existing processed information where possible and only perform work that is required for newly added data.

---

## Pipeline Stages

The master runner executes the following stages:

1. `Deliverable3_DataPrep.py` — prepares newly available monthly Airbnb data.
2. `Deliverable3_Concatenate.py` — rebuilds the combined Christchurch dataset.
3. `Deliverable4_DataCleaning.py` — cleans and validates the combined Airbnb dataset.
4. `area_code.py` — reuses or extends the Stats NZ SA2 coordinate lookup.
5. `Deliverable5_areaoperations.py` — runs the Airbnb-versus-rental-bond analysis for supported reporting periods.
6. `Deliverable3_SummaryStats.py` — regenerates summary statistics.
7. `Deliverable3_Visualisations.py` — regenerates visual outputs.

The runner uses the same Python environment that launched it and stops if one of the stages fails.

---

## Monthly Data Processing

The monthly preparation and concatenation stages are designed to work with the available monthly Airbnb files rather than requiring the month list to be manually rewritten for every update.

The combined Christchurch dataset is written to:

```text
data/processed/christchurch_listings_combined.csv
```

The cleaning stage then produces:

```text
data/processed/christchurch_listings_combined_cleaned.csv
```

Using stable filenames allows later stages of the pipeline to continue working as additional months are added.

---

## Data Cleaning

The Airbnb cleaning stage reads the combined dataset and applies the same cleaning rules used previously, including:

- handling missing identifier and host fields
- handling missing review-related values
- handling missing `minimum_nights`
- removing rows with missing prices
- excluding prices above the defined price cap
- removing unnecessary columns
- validating row accounting and output integrity

The cleaning audit is calculated from the current data rather than assuming a fixed number of rows.

Months where all price values are missing are also identified dynamically in the audit output.

---

## Incremental Spatial Enrichment

Airbnb listings contain latitude and longitude but require Stats NZ SA2 area codes for geographic analysis.

The pipeline uses:

```text
data/processed/Christchurch_coordinate_area_lookup.csv
```

as a persistent coordinate-to-SA2 lookup cache.

Before querying Koordinates, the script:

1. extracts the unique coordinate pairs in the current cleaned Airbnb dataset;
2. normalises the coordinates using the pipeline's coordinate-rounding rule;
3. loads previously successful coordinate mappings;
4. compares the current coordinates with the cached coordinates;
5. queries only coordinates that have not already been successfully resolved.

Successful new mappings are added to the cache.

Failed coordinates are not treated as successfully resolved and may therefore be retried during a later run.

### Repeat-run behaviour

For the current dataset:

```text
Unique coordinate pairs: 3927
Already cached: 3927
New to query: 0
Persistent lookup entries: 4095
```

This demonstrates that once the spatial cache has been updated, repeating the pipeline does not unnecessarily repeat Koordinates API requests.

---

## Koordinates API Key

The Koordinates API key is treated as a local credential and is not stored in the repository.

Each user can create a local `.env` file in the repository root containing:

```text
KOORDINATES_API_KEY=YOUR_API_KEY
```

Install the environment-variable loader in the active Python environment if required:

```bash
python -m pip install python-dotenv
```

`python-dotenv` loads the value when required.

The `.env` file is excluded from Git.

An API key is only needed when the pipeline encounters coordinates that are not already successfully stored in the lookup cache.

---

## Spatial Validation

The spatial-enrichment stage includes sanity checks to detect inconsistent results.

These include:

- checking that coordinates fall within the expected regional bounds;
- checking that coordinate lookup keys are unique;
- calculating the spatial lookup match rate;
- enforcing a minimum acceptable match rate;
- checking that the Airbnb row count is preserved during the spatial merge;
- using a many-to-one merge validation to prevent duplicate lookup coordinates from multiplying Airbnb observations.

The current enriched dataset contains an area code for every cleaned Airbnb row.

---

## Scrape-Date Metadata

The `days_since_last_review` calculation requires the date associated with each monthly Inside Airbnb dataset.

Previously these dates were embedded directly in the visualisation script.

They are now stored separately in:

```text
config/airbnb_scrape_dates.csv
```

The visualisation stage merges these dates onto the combined Airbnb dataset using `month_year`.

If a month exists in the Airbnb data but does not have corresponding scrape-date metadata, the script stops with an error rather than calculating the metric using an assumed date.

The July and August 2026 datasets use the Inside Airbnb dates:

```text
2026-07 -> 2026-07-12
2026-08 -> 2026-08-13
```

---

## Summary Statistics and Visualisations

Downstream analysis scripts now read the stable combined Christchurch dataset rather than filenames containing a fixed end month.

The automated workflow also runs the Airbnb-versus-rental-bond analysis after spatial enrichment. This stage uses only Airbnb observations whose calendar quarter has a corresponding reporting period in the cleaned rental-bond dataset.

The summary-statistics stage also reports missing values by month and generates:

```text
outputs/missing_values_by_month.png
```

The existing Deliverable 3 visualisations remain focused on the original analysis tasks, including:

- New Zealand Airbnb price distribution;
- Christchurch Airbnb price distribution;
- comparison of New Zealand and Christchurch price distributions;
- distribution of `days_since_last_review`;
- calculation of the top 10% of listings by number of reviews.

---

## Repeatability Test

The complete pipeline was run successfully from:

```bash
python scripts/run_airbnb_pipeline.py
```

It was then run again without changing the input data.

The second run:

- completed successfully;
- did not duplicate the monthly combined data;
- reused all existing spatial mappings;
- required 0 new Koordinates queries;
- regenerated the downstream outputs.

This confirms that the workflow can be rerun on demand rather than requiring the previous deliverable steps to be manually repeated.

---

## Rental Bond Analysis Scope

The Airbnb-versus-rental-bond analysis is included in the automated pipeline.

Airbnb `month_year` values are converted dynamically to their calendar-quarter start dates. These dates are then compared with the reporting periods actually available in the cleaned rental-bond dataset.

Only Airbnb observations whose quarter has corresponding rental-bond data are included in the comparison.

For the current datasets, July and August 2026 remain part of the main Airbnb pipeline but are excluded from the rental-bond comparison because the cleaned bond dataset does not contain a matching July 2026 reporting period.

This prevents rental-bond values from being invented or carried forward into unsupported periods.

If a future cleaned rental-bond dataset contains the corresponding reporting quarter, the relevant Airbnb observations can enter the comparison without extending another hard-coded month mapping.