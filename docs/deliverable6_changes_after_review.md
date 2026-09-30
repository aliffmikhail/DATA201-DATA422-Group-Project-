# Deliverable 6 - Changes After Code Review

## Purpose

This document records the high-level code review completed for Deliverable 6.

The purpose of the review was to compare the existing project code against the coding and software design practices selected by the team.

For each reviewed component, this document records:

- the file or pipeline stage reviewed,
- the coding practice considered,
- whether a change was required,
- what was changed,
- and why the change was made.

The changes are documented at a high level rather than line-by-line.

---

## Review Summary

| Component | Reviewer | Main Practices Reviewed | Review Outcome |
| --- | --- | --- | --- |
| `scripts/Deliverable5_areaoperations.py` | Muhammad Aliff Mikhail Bin Norkamarulazhar | Sanity checking, self-documenting code, clear pipeline interfaces | Reviewed; no additional Deliverable 6 code changes required |
| `scripts/area_code.py` | Asfa Hurin Binti Asmawi | Self-documenting code, sanity checking, file headers | File header and spatial validation function added |
| Other pipeline components | Other assigned team members | To be completed | Pending |

---

# Deliverable 5 Integration Review

## File Reviewed

`scripts/Deliverable5_areaoperations.py`

## Reviewer

Muhammad Aliff Mikhail Bin Norkamarulazhar

## Coding Practices Considered

- sanity checking,
- self-documenting code,
- clear interfaces between pipeline stages,
- reuse of intermediate outputs.

## Review Outcome

No additional code changes were required during the Deliverable 6 review.

The existing implementation already contained the main practices selected for this section of the pipeline.

---

## Existing Practices Confirmed During Review

### 1. Final Processed Datasets Are Used as Pipeline Inputs

The integration stage uses the final cleaned Airbnb and rental bond datasets produced by earlier pipeline stages.

This provides a clear interface between the cleaning stages and the final data-integration stage.

The Deliverable 5 analysis uses:

- the final cleaned Airbnb dataset,
- the final cleaned rental bond dataset,
- and the previously saved geographic area-code mapping.

This makes the pipeline more reproducible and reduces reliance on unexplained intermediate files.

### 2. Saved Geographic Mapping Is Reused

The geographic mapping generated from the Koordinates API is reused rather than queried again.

This avoids unnecessary external API requests and makes the pipeline faster and easier to reproduce.

### 3. Output Names Are Self-Documenting

The integration script uses descriptive names such as:

- `Median_Gap`
- `Maximum_Gap`
- `Observations`
- `matched_percent`
- `Daily_Rent`

These names communicate the purpose of each value more clearly than vague or informal names.

### 4. The Data Join Is Explicitly Validated

The integration stage checks:

- missing `TimeFrame` values,
- duplicate rental-bond location-time keys,
- row counts before and after the join,
- matched and unmatched observations,
- overall match percentage.

These checks help detect integration problems even when the merge itself runs successfully.

---

# Sanity Check Example - Airbnb and Rental Bond Join

## Expected Behaviour

Each Airbnb observation should match at most one overall rental bond record for the same:

- geographic area,
- and reporting period.

Therefore, the join should not increase the number of Airbnb observations.

## Observed Results

- Airbnb rows before join: 18,080
- Rows after join: 18,080
- Duplicate bond location-time keys: 0
- Matched Airbnb observations: 13,821
- Unmatched Airbnb observations: 4,259
- Match rate: 76.4%

## Interpretation

The unchanged row count provides evidence that the join did not accidentally multiply Airbnb observations.

The duplicate-key check supports the expected many-to-one relationship between Airbnb observations and rental bond records.

The match-rate calculation also makes unmatched data visible rather than silently discarding those observations.

---

# Geographic Mapping Review

## File Reviewed

`scripts/area_code.py`

## Reviewer

Asfa Hurin Binti Asmawi

## Coding Practices Considered

The review focused on three coding practices:

- self-documenting code,
- sanity checking,
- file headers.

The existing file paths, input/output structure, API calls, and core pipeline dependencies were intentionally left unchanged.

This minimised disruption to the existing pipeline while improving documentation and validation.

---

## Changes Made

### 1. File Header Added

A structured file header was added to the beginning of `area_code.py`.

The header documents:

- the purpose of the script,
- its main dependencies,
- the expected inputs,
- and the outputs produced by the script.

### Reason

The file header makes the role of `area_code.py` easier for another team member to understand without having to inspect the entire script.

This supports the use of self-documenting code and improves maintainability.

---

### 2. Spatial Validation Function Added

A dedicated validation function named:

`validate_spatial_data()`

was added to perform runtime sanity checks on the geographic mapping stage.

The validation focuses on:

- coordinate bounds,
- spatial lookup success rate,
- and row-count integrity.

---

## Spatial Sanity Checks

### Check 1 - Geographic Coordinate Bounds

The validation checks whether Airbnb coordinates fall inside the expected Canterbury/Christchurch geographic range.

The bounds used are approximately:

- latitude: `-44.2` to `-43.2`
- longitude: `171.8` to `173.5`

Rows outside these bounds are identified and reported.

### Reason

This helps detect obviously invalid or unexpected geographic coordinates before relying on them for spatial mapping.

For example, coordinates located far outside Canterbury could indicate a data-quality or processing problem.

---

### Check 2 - Koordinates Lookup Match Rate

The validation calculates the percentage of spatial lookup results that contain a non-missing `area_code`.

Conceptually:

`Spatial Lookup Match Rate = successful area-code matches / total lookup records`

The script prints the resulting match percentage.

A minimum threshold of 50% is used as an assertion.

If the success rate falls below the threshold, the validation fails.

### Reason

A very low spatial lookup success rate could indicate:

- incorrect coordinates,
- an API problem,
- an incorrect layer,
- or another mapping issue.

The assertion therefore provides an early warning if the geographic mapping stage is not functioning as expected.

---

### Check 3 - Row-Count Integrity

The validation checks that the expected number of rows is preserved after the spatial mapping stage.

The intention is to detect accidental data loss or unexpected row-count changes during the mapping or merge process.

### Reason

A mapping operation may run successfully while still accidentally removing or duplicating observations.

Checking the row count gives an additional safeguard against this type of pipeline error.

---

## Minimal-Disruption Strategy

The review intentionally avoided changing the core behaviour of `area_code.py`.

The following parts were retained:

- existing file paths,
- existing input/output structure,
- Koordinates API configuration,
- geographic lookup process,
- saved output files,
- dependencies used by later pipeline stages.

Only documentation and validation behaviour were added.

### Reason

The geographic mapping stage had already been used successfully by later deliverables.

Changing its core implementation during Deliverable 6 could introduce unnecessary compatibility problems.

The review therefore focused on improving clarity and validation while preserving the existing pipeline interface.

---

# Relationship Between the Two Reviews

The two reviewed components demonstrate different parts of the project pipeline.

`area_code.py` is responsible for creating the geographic key required to connect Airbnb observations with the rental bond data.

Its Deliverable 6 review therefore focused on validating the spatial mapping stage before its outputs are used later in the pipeline.

`Deliverable5_areaoperations.py` uses the geographic mapping and the cleaned datasets to perform the final integration.

Its review therefore focused on validating the join, checking row-count behaviour, and making the resulting analysis easier to interpret.

Together, these reviews add sanity checks at two important stages:

1. before geographic mapping results are relied upon,
2. and when the final datasets are joined.

---

# Review Principles

The team followed the following principles while reviewing the code:

1. Changes should only be made where they provide a clear improvement.
2. Existing code should not be rewritten simply to demonstrate that a review occurred.
3. Reviews should consider the role of each file within the wider pipeline.
4. Changes should be documented at a high level rather than line-by-line.
5. The reason for each change should be recorded alongside the change.
6. Sanity checks should test meaningful expectations about the data or pipeline behaviour.
7. Existing pipeline interfaces should be preserved where possible to avoid breaking later stages.
8. If a component already follows the selected coding practices, the review may conclude that no additional change is required.

---

### File or Component Reviewed

Deliverable4_DataCleaning.py script.

### Reviewer

Abdurrahman Rais Fadhil

### Coding Practices Considered

- **File Header:** Added description on the top of the code to describe the input, output and how the code works.

- **Self-documenting code:** a structured module header describing purpose, dependencies, inputs, outputs and processing steps.


### Changes Made

1. Added a structured production header documenting the script's purpose, dependencies (Python 3, pandas, os), inputs (file path and required and optional columns), outputs (cleaned CSV and console report), processing steps, and sanity-check behavior.
2. Added a `REQUIRED_COLUMNS` constant listing the columns the cleaning logic depends on.
3. Added a `_require(condition, message)` helper that raises a `ValueError` prefixed with "Sanity check failed:".
4. Added sanity checks before loading, after loading, after each cleaning step, and after export (listed under Sanity Checks).
5. Left unchanged: the function signature, `FILE_PATH` / `OUTPUT_PATH`, all cleaning logic, the price cap, audit report text, and output file format.

### Reason for Changes

The original script only checked that the input file existed. Several realistic data problems would have passed through unnoticed or failed with unclear errors:

- A price stored as text (e.g. `"$120.00"`) would break the price filter with a confusing pandas comparison error.
- A header-only CSV would crash with a `ZeroDivisionError` in the retention-rate calculation.
- A missing column would raise a bare `KeyError` with no context.
- Negative or impossible values would be written silently to the cleaned dataset.
- An output path equal to the input path would overwrite the raw data.

The new checks turn these into immediate, descriptive errors. The header makes the script's purpose and contract clear to anyone maintaining or reusing it.

### Sanity Checks

**Before loading**
- `file_path` and `output_path` are non-empty strings.
- `output_path` is not the same as `file_path` (protects the raw input).
- The input exists, is a file, and is not 0 bytes.

**After loading**
- The dataset contains at least one data row (this also prevents division by zero in the retention rate).
- All required columns are present: `id`, `host_id`, `host_name`, `reviews_per_month`, `minimum_nights`, `price`.
- `price`, `reviews_per_month` and `minimum_nights` are numeric dtypes.
- No negative `price` or `reviews_per_month`, and no `minimum_nights` below 1.

**After filling missing values**
- The `minimum_nights` median exists, so the column isn't entirely empty.
- No nulls remain in the filled columns.
- The row count is unchanged.

**After dropping columns**
- `license` and `neighbourhood_group` are gone.
- All required columns are still present.

**After price cleaning**
- No missing prices remain.


# Remaining Team Reviews

Additional sections can be added below as the remaining team members complete their assigned reviews.

## Additional Pipeline Review

### File or Component Reviewed

scripts/Deliverable3_Visualization.py

### Reviewer

Dron Dalvi

### Coding Practices Considered

- Help collaboration
- Save Time
- Mark sections  

### Changes Made

- Added comments to explain each part of the code 

### Reason for Changes

- To help third person to understand what's happening in the code who have no idea about it 

### Sanity Checks

_To be completed._
