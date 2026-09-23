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
- Temporal Scope: Restricted to March through November due to systemic missing data in peak summer records.
- Feature Reduction: Zero-variance and fully empty columns removed to streamline downstream analysis.

## Changes Made & Cleaning Justification
1. Price Filtering:
   - Dropped all rows with missing price values (imputing 37% of the dataset would distort downstream variance).
   - Filtered extreme price outliers (records >$1,500 or identified via IQR) to remove data entry typos and non-standard luxury properties.
2. Temporal Scope Adjustment (month_year):
   - Identified 100% data was loss for summer peak months (Dec 2025, Jan 2026, Feb 2026) due to collection failure.
   - Explicitly restricted dataset scope to March-November.
3. Column Deletions:
   - Removed license due to 100% missing values (zero informational value).
   - Removed neighbourhood_group as it contained a constant value ("Christchurch City") across all records (zero variance). 
4. Logical Imputations:
   - Imputed reviews_per_month with 0.0 for 2,627 missing rows (9.1% of dataset) where total reviews equaled zero (last_review left blank).
   - Imputed minimum_nights missing values (37 rows/0.1%) with the dataset median of 1.0 night.
   - Imputed a single missing host_name value with the string "Unknown". 

## Expected Output
- Dataset Size: Final clean dataset contains 18,080 rows (reduction of 10,667 missing-price rows and ~150-300 outlier rows).
- Feature Count: Two fewer columns following the removal of license and neighbourhood_group.
- Analytical Scope: Comparative analysis is strictly bounded to March-November pricing patterns.
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
| 5 | Total Bonds | int64 | otal number of tenancy bonds lodged with Tenancy Services during the reference period. |
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
Expected Dimensions: 26,991 rows × 12 columns (pending final script verification execution).



