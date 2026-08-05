# DATA201-DATA422-Group-Project-
DATA201 | DATA422 Group Project 

## Team Members
- Muhammad Aliff Mikhail Bin Norkamarulazhar
- Asfa Hurin Binti Asmawi
- Dron Vihang Dalvi
- Abdurrahman Rais Fadhil. I'm a DATA422 student. This changes is for the branch in order to merge this branch to main.

# Week 3: Airbnb Listings Analysis

## Data Source:
The dataset used in this project is sourced from Inside Airbnb, an independent, non-commercial open-data initiative that provides data on Airbnb listings, availability, and guest reviews across major global cities.

### File Name:
listings.csv

## Data Dictionary:
| Column Num | Column | Name Data Type | Description |
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













