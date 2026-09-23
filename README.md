# DATA201-DATA422-Group-Project-
DATA201 | DATA422 Group Project 

## Team Members:
- Muhammad Aliff Mikhail Bin Norkamarulazhar (DATA201)
- Asfa Hurin Binti Asmawi (DATA201)
- Dron Vihang Dalvi (DATA422)
- Abdurrahman Rais Fadhil (DATA422)

# Airbnb Listings Analysis

## Data Source
- Provider: Sourced from Inside Airbnb, an independent, non-commercial open-data initiative.
- Coverage: Provides data on Airbnb listings, availability, and guest reviews across major global cities.
- File Name: listings.csv

## Data Dictionary
| Column Num | Column | Data Type | Description |
| ----- | ----- | ----- | ----- |
| 1 | id | Integer/String | Unique identifier assigned by Airbnb for the listing. |
| 2 | name | String | Public name or title of the listing as defined by the host. |
| 3 | host_id | Integer | Unique identifier for the host user. |
| 4 | host_name | String | First name (or display name) of the host. |
| 5 | neighbourhood_group | String | Broader region, borough, or municipality group (may be blank/null for some areas). |
| 6 | neighbourhood | String | Specific neighborhood, district, or local area of the listing. |
| 7 | latitude | Float | World Geodetic System (WGS84) latitude coordinate of the listing. |
| 8 | longitude | Float | World Geodetic System (WGS84) longitude coordinate of the listing. |
| 9 | room_type | String | Categorization of the space offered (Entire home/apt, Private room, Shared room, or Hotel room). |
| 10 | price | Numeric / Currency | Nightly rental price (in local currency). |
| 11 | minimum_nights | Integer | Minimum required length of stay in nights. |
| 12 | number_of_reviews | Integer | Total cumulative count of guest reviews received by the listing. |
| 13 | last_review | Date (YYYY-MM-DD) | Date of the most recent guest review.|
| 14 | reviews_per_month | Float | Average calculated number of reviews received per month over the listing's lifetime. |
| 15 | calculated_host_listings_count | Integer | Total number of listings managed by the host in this region. |
| 16 | availability_365 | Integer | Total number of days the listing is available for booking within the next 365 days. |
| 17 | number_of_reviews_ltm | Integer | Number of reviews received by the listing within the last 12 months. |
| 18 | license | String | Local permit, registration, or business license number (if required/provided). |

## Data Notes
### Location Privacy
- Latitude and longitude coordinates are masked by Airbnb for privacy.
- Coordinates are randomly shifted within a range of 0 to 150 meters from the ture property location.

### Missing Values
- Null/NaN values occur in columns such as neighbourhood_group, last_review, reviews_per_month, and license.
- Missingness depends on listing activity levels and local municipal regulatory requirements.

# Data Cleaning Documentation Summary

## Airbnb Listings Data Cleaning
- Objective: Prepare the Airbnb dataset for comparative price metric analysis.
- Volume Change: Reduced from 28,795 rows to 18,080 rows.
- Temporal Scope: Covers the cleaned Christchurch Airbnb observations from October 2025 through June 2026.
- Feature Reduction: Zero-variance and fully empty columns removed to streamline downstream analysis.

## Changes Made & Cleaning Justification
1. Price Filtering:
   - Dropped all rows with missing price values (imputing 37% of the dataset would distort downstream variance).
   - Filtered extreme price outliers (records >$1,500 or identified via IQR) to remove data entry typos and non-standard luxury properties.
2. Temporal Scope (month_year):
   - Retained the cleaned Christchurch Airbnb observations covering October 2025 through June 2026.
   - The month_year field is later used in Deliverable 5 to align Airbnb observations with rental bond reporting periods.
3. Column Deletions:
   - Removed license due to 100% missing values (zero informational value).
   - Removed neighbourhood_group as it contained a constant value ("Christchurch City") across all records (zero variance). 
4. Logical Imputations:
   - Imputed reviews_per_month with 0.0 for 2,627 missing rows (9.1% of dataset) where total reviews equaled zero (last_review left blank).
   - Imputed minimum_nights missing values (37 rows/0.1%) with the dataset median of 1.0 night.
   - Imputed a single missing host_name value with the string "Unknown". 

## Expected Output
- Dataset Size: Final clean dataset contains 18,080 rows after missing-price and outlier filtering.
- Feature Count: Two fewer columns following the removal of license and neighbourhood_group.
- Analytical Scope: Comparative analysis uses the cleaned Airbnb observations from October 2025 through June 2026.
- Data Integrity: Protected unique identifier keys from rounding errors and logically handled missing numeric metrics without row inflation.


# Rental Bond Cleaning

## Source and purpose
* Provider: Tenancy Services, New Zealand
* Dataset: Detailed quarterly rental bond report (2020-2026)
* Source: https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/
* Raw File Path: data/raw/rental_bond_detailed_2020_2026.csv
* Cleaning Script: scripts/Deliverable4_BondCleaning.py
* Scope & Context:
  - Documents private-sector tenancy bonds organised by tenancy start date and SA2-2019 geographical definitions.
  - Bond counts are rounded to base 3; categories with fewer than 5 bonds are suppressed by the provider.

## Data Dictionary
| Column Num | Column | Data Type | Working Description |
| ----- | ----- | ----- | ----- |
| 1 | TimeFrame | string | Reporting reference start date for the quarterly bond summary (e.g., 2020-01-01 to 2026-04-01). |
| 2 | Location Id | float64 | Statistical Area 2 (SA2 2019) geographic code (includes special code -99 for unassigned locations). |
| 3 | Dwelling Type | string | Property structure category (ALL, Apartment, Boarding House, Flat, House, Room). |
| 4 | Number Of Beds | string | Bedroom count per listing (1, 2, 3, 4, 5, 5+, ALL, or missing/null). |
| 5 | Total Bonds | int64 | Total number of tenancy bonds lodged with Tenancy Services during the reference period. |
| 6 | Active Bonds | int64 | Cumulative count of active bonds held at the end of the reference period. |
| 7 | Closed Bonds | int64 | Total number of tenancy bonds refunded/closed during the reference period. |
| 8 | Median Rent | float64 | Median weekly rental price in NZD ($). |
| 9 | Geometric Mean Rent | float64 | Geometric mean weekly rental price in NZD ($), dampening the effect of extreme values. |
| 10 | Upper Quartile Rent | float64 | Upper quartile (75th percentile) weekly rental price in NZD ($). |
| 11 | Lower Quartile Rent | float64 | Lower quartile (25th percentile) weekly rental price in NZD ($). |
| 12 | Log Std Dev Weekly Rent | float64 | Standard deviation of log-transformed weekly rent, measuring price dispersion. |
* This is not a provider-issued data dictionary. The precise statistical and aggregate definitions remain unverified.

## Processing, Evidence, and Limitations

### Cleaning Steps & Row Counts
| Num | Step | Rows / effect |
| ----- | ----- | ----- |
| 1 | Original raw dataset | 226,080 rows x 12 columns. |
| 2 | Convert TimeFrame; filter Oct 2025-Jun 2026 | 27,212 rows retained; 198,868 excluded. Dates present: 2025-10-01, 2026-01-01, 2026-04-01. |
| 3 | Remove missing Location Id | 94 rows excluded because no geographic match is possible; these also lack median rent. 27,118 rows remain. |
| 4 | Exclude Location Id = -99 | 127 more records excluded from the ordinary-location dataset because mapping is unverified. Expected final: 26,991 rows x 12 columns. |

### Missing and Special Values
- Pre-Filtering Missingness: 94 missing Location Id records, 890 missing Number Of Beds records, and 94 missing values across all five rent-statistic fields.
- Co-occurrence: The 94 records with missing Location Id directly corresponded to the 94 missing rent statistic entries.
- Temporal Concentration: 819 of the 890 missing bedroom values occurred in the October 2025 period.
- Treatment: Missing bedroom values are retained as NaN without imputation; aggregate "ALL" category values are explicitly retained.

### Checks and Treatment of Outliers
- Data Audits: Inspected for exact duplicates, negative bond counts, non-positive rent values, and quartile ordering errors.
- Uniqueness Validation: Composite-key uniqueness checks implemented using TimeFrame + Location Id + Dwelling Type + Number Of Beds.
- Outlier Policy: Genuine extreme rental values are preserved to reflect true market variation rather than treated as errors.
- Export and Reproduction
Output Path: data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv
Final Dimensions: 26,991 rows × 12 columns.

# Deliverable 5 - Airbnb and Rental Bond Integration

## Geographic Area Mapping

Airbnb listings contain latitude and longitude coordinates but do not contain the `Location Id` used by the rental bond dataset.

`scripts/area_code.py` uses the Koordinates Query API to obtain Stats NZ SA2 area codes from Airbnb coordinates.

The script:

1. loads the Christchurch Airbnb data,
2. extracts unique latitude/longitude pairs,
3. queries Koordinates for an SA2 area code,
4. saves the coordinate-to-area-code lookup,
5. merges the area codes back onto the Airbnb records.

The Koordinates API key is read from the local `KOORDINATES_API_KEY` environment variable and is not stored in the repository.

Saved mapping files:

- `Christchurch_coordinate_area_lookup.csv`
- `Christchurch_Airbnb_with_area_codes.csv`

Mapping validation:

- 3,957 unique coordinate pairs
- 0 duplicate coordinate pairs
- 0 missing area codes in the lookup
- 0 missing area codes after transferring the mapping onto the final cleaned Airbnb dataset

The saved area-code results are reused rather than repeating the API requests.

## Datasets Used

Airbnb:

`data/processed/christchurch_listings_2025_10_to_2026_06_cleaned.csv`

- 18,080 cleaned listing-month observations

Rental bonds:

`data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv`

- 26,991 rows
- 12 columns

## Time Alignment

Airbnb data are monthly while the rental bond data use reporting reference dates.

The Airbnb months are aligned as follows:

| Airbnb months | Bond TimeFrame |
| --- | --- |
| Oct-Dec 2025 | 2025-10-01 |
| Jan-Mar 2026 | 2026-01-01 |
| Apr-Jun 2026 | 2026-04-01 |

All 18,080 Airbnb observations were successfully assigned a TimeFrame.

## Rental Bond Preparation

The bond dataset contains multiple dwelling and bedroom categories for the same location and reporting period.

For the general location-level comparison, the analysis uses records where:

- `Dwelling Type = ALL`
- `Number Of Beds = ALL`

This produces one overall bond record per location and reporting period and avoids averaging subgroup medians or summing overlapping categories.

Validation:

- 4,865 location-time records
- 0 duplicate `Location Id + TimeFrame` combinations
- 0 missing median rent values

Weekly median rent is converted to a daily equivalent:

`Daily Rent = Median Rent / 7`

## Dataset Join

`scripts/Deliverable5_areaoperations.py` joins Airbnb and rental bond data using:

- Airbnb `area_code` / bond `Location Id`
- `TimeFrame`

A left join is first used for validation so unmatched Airbnb records remain visible.

Join results:

- Airbnb rows before join: 18,080
- Rows after join: 18,080
- Matched rows: 13,821
- Unmatched rows: 4,259
- Match rate: 76.4%

The unchanged row count confirms that the join does not multiply Airbnb observations.

Only matched records are used for the rental price comparison.

## Christchurch Central Airbnb Price

Christchurch Central uses area code `326600`.

Using the cleaned Airbnb dataset:

- Median Airbnb nightly price: **NZ$238**

## Short-Term vs Long-Term Rental Price Gap

For each matched Airbnb observation:

`Rent Gap = Airbnb Nightly Price - Daily Long-Term Rent`

The analysis calculates:

- `Median_Gap` - typical price gap within an area
- `Maximum_Gap` - largest single observed price gap
- `Observations` - number of matched observations supporting the result

Current results:

- Area `322800` has the largest median gap at approximately **NZ$243.64 per night**, based on 6 observations.
- Area `326100` contains the largest single observed gap at **NZ$1,435 per night**, based on 201 observations.

The number of observations should be considered when interpreting area-level results.

## Airbnb and Rental Bond Counts

Airbnb supply is represented by the number of unique Airbnb listing IDs within each area and reporting period.

Long-term rental activity is represented using `Active Bonds` from the corresponding overall bond record.

`Active Bonds` refers to active rental bonds and should not be interpreted as the number of vacant or currently available rental properties.

## Limitations

The Airbnb mapping uses the Stats NZ SA2 2026 geographic field, while the rental bond source documentation refers to SA2-2019 geographic definitions.

This difference may contribute to unmatched area codes and should be considered when interpreting the 76.4% join rate.

Airbnb prices are advertised nightly short-term accommodation prices, while rental bond median rents represent weekly long-term rental prices. Dividing weekly rent by seven provides a daily comparison unit, but the two values still represent different rental markets.
