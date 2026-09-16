# DATA201-DATA422-Group-Project-
DATA201 | DATA422 Group Project 

## Team Members:
- Muhammad Aliff Mikhail Bin Norkamarulazhar
- Asfa Hurin Binti Asmawi
- Dron Vihang Dalvi
- Abdurrahman Rais Fadhil. I'm a DATA422 student.

# Airbnb Listings Analysis:

## Data Source:
The dataset used in this project is sourced from Inside Airbnb, an independent, non-commercial open-data initiative that provides data on Airbnb listings, availability, and guest reviews across major global cities.

### File Name:
listings.csv

## Data Dictionary:
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

## Data Notes:

### Location Privacy:
Latitude and longitude coordinates are masked by Airbnb for privacy, usually randomized within 0-150 meters of the actual property location.

### Missing Values:
Columns like neighbourhood_group, last_review, reviews_per_month, and license may contain NaN/null values depending on listing activity and local regional requirements.

# Data Cleaning Documentation Summary:

## Summary
The objective of this data cleaning process was to prepare the Airbnb dataset for comparative analysis, focusing primarily on price metrics. The initial dataset contained 28,795 rows. Due to significant missing values in core target metrics—specifically the price field and peak summer season records—strict filtering was applied to preserve statistical validity. The final cleaned dataset contains 18,080 rows spanning from March to November, with zero-variance and entirely empty features completely removed to streamline downstream analysis.

## Changes Made & Cleaning Justification
Several critical structural changes and data modifications were executed based on the column evaluations. For the price column, all rows with missing values were dropped because it is the core target metric for comparison, and imputing 37% of the dataset would severely distort downstream variance. Extreme price outliers (such as records exceeding $1,500 or calculated via the IQR method) were filtered out to prevent data entry typos or non-standard luxury bookings from heavily skewing mean calculations. For the month_year field, a systemic data collection failure was acknowledged for the summer peak months of Dec 2025, Jan 2026, and Feb 2026; since 100% of this summer pricing data was lost, the dataset is documented as restricted to a specific temporal window.
To improve dataset efficiency, the license column was dropped entirely because it contained 100% missing data and provided zero informational value. Similarly, the neighbourhood_group column was removed after verifying both datasets covered the same area, as its constant value ("Christchurch City" across all rows) added zero analytical variance. 

Missing entries in other columns were addressed using targeted logical imputations. For the 2,627 missing rows in last_review and reviews_per_month (representing 9.1% of the total dataset), reviews_per_month was imputed with 0.0 while leaving last_review blank, since these entries perfectly matched properties with zero total reviews. The 37 missing values in minimum_nights (0.1% of rows) were imputed using the dataset median of 1.0 night to safely handle extreme 365-night max outliers without distorting the data. Finally, a single missing value in the host_name column was imputed with the literal string "Unknown," bypassing an unnecessary row deletion for a minor descriptive omission.

## Expected Output
The final cleaned dataset experiences a reduction in volume, dropping from the initial 28,795 rows down to 18,080 rows. This includes the definitive loss of 10,667 rows with missing prices, alongside a minor loss of an estimated 150 to 300 rows due to outlier filtering. The dataset contains two fewer features after the total removal of the license and neighbourhood_group columns. Temporally, the scope of any subsequent analysis is strictly limited to comparing prices from March to November due to the summer peak data collection failure. Ultimately, the data is structurally sound, unique identifier keys are protected from rounding errors, and missing numeric metrics are logically handled without inflating row counts.


# Rental Bond Cleaning:

## Source and purpose:
* Provider: Tenancy Services, New Zealand.
* Dataset: Detailed quarterly rental bond report, 2020-2026
* Source: https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/
* Raw file: data/raw/rental_bond_detailed_2020_2026.csv
* Code: scripts/Deliverable4_BondCleaning.py

The source describes private-sector tenancy bonds, organised by tenancy start date and SA2-2019 geographical definitions. It documents rounding to base three and suppression where fewer than five bonds meet a selection. These disclosures do not establish the cause of any particular missing value.

## Data Dictionary:
| Column Num | Column | Data Type | Working Description |
| ----- | ----- | ----- | ----- |
| 1 | TimeFrame | string | Reporting reference date; exact quarter coverage not confirmed. |
| 2 | Location Id | float64 | Geographic identifier; special -99 code not mapped. |
| 3 | Dwelling Type | string | Dwelling category; includes ALL. |
| 4 | Number Of Beds | string | Bedroom category; includes ALL and missing values. |
| 5 | Total Bonds | int64 | Reported total bond count. |
| 6 | Active Bonds | int64 | Reported active bond count; not a vacancy count. |
| 7 | Closed Bonds | int64 | Reported closed bond count. |
| 8 | Median Rent | float64 | Median rent statistic. |
| 9 | Geometric Mean Rent | float64 | Geometric mean rent statistic. |
| 10 | Upper Quartile Rent | float64 | Upper-quartile rent statistic. |
| 11 | Lower Quartile Rent | float64 | Lower-quartile rent statistic. |
| 12 | Log Std Dev Weekly Rent | float64 | Log-scale weekly-rent variability measure. |
* This is not a provider-issued data dictionary. The precise statistical and aggregate definitions remain unverified.

## Processing, evidence, and limitations:

### Cleaning steps and row counts:
| Num | Step | Rows / effect |
| ----- | ----- | ----- |
| 1 | Original dataset | 226,080 rows x 12 columns. |
| 2 | Convert TimeFrame; filter Oct 2025-Jun 2026 | 27,212 rows retained; 198,868 excluded. Dates present: 2025-10-01, 2026-01-01, 2026-04-01. |
| 3 | Remove missing Location Id | 94 rows excluded because no geographic match is possible; these also lack median rent. 27,118 rows remain. |
| 4 | Exclude Location Id = -99 | 127 more records excluded from the ordinary-location dataset because mapping is unverified. Expected final: 26,991 rows x 12 columns. |

### Missing and special values:
Before row removal: 94 missing Location Id, 890 missing Number Of Beds, and 94 missing values in each of the five rent-statistic fields. The same 94 missing-ID records also lacked median rent; 819 missing-bed records occurred in October 2025. The remaining missing-bedroom values are kept as NaN, without imputation. ALL values in both category columns are retained and must not be confused with missingness. The exact causes of missing values and meaning of -99 remain unverified.

### Checks and treatment of outliers:
Previous inspection found zero exact duplicate rows, negative bond counts, non-positive checked rent values and invalid quartile ordering. The revised script should also check proposed composite-key uniqueness using TimeFrame + Location Id + Dwelling Type + Number Of Beds and print the observed median-rent minimum/maximum. Do not claim those new checks passed until they have been run. Do not delete unusual rents simply because they are extreme.

### Export and reproduction:
Expected output: data/processed/rental_bond_cleaned_2025_10_to_2026_04.csv (26,991 rows x 12 columns, pending verification).

























