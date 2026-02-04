# Open Door Plan 🏙️
## By team: Keys to the City 
[Vincent Perez](https://www.linkedin.com/in/thevinceperez/), [Thomas Segal](https://www.linkedin.com/in/thomas-segal-093370369/) and [Kevin Serrano Lopez](https://www.linkedin.com/in/kevin-serrano-lopez/)
## CRQ:
Using government and non-profit owned housing as a proxy for affordability, is variation in the monthly counts of demolition job records predictive of changes in New York City’s shelter population over time, accounting for seasonality, from 2015 to 2024?\
## Hypothesis  
We hypothesize that higher monthly counts of public housing demolition job records will be predictive of increases in the NYC shelter population, potentially with a lag of several months.\
Below is a polished, README-ready version that keeps an analyst / student tone and clearly documents data provenance, structure, and intended use.


## Data Sources Overview

This project uses two primary New York City government datasets to examine the relationship between residential building demolitions and trends in homelessness over time. Together, these datasets support exploratory data analysis (EDA) and time-series modeling to assess whether demolitions—particularly of government and non-profit (affordable) housing—are associated with changes in shelter populations.



## Data Source 1: NYC Department of City Planning (DCP) – Housing Database

**Source:**
[NYC Department of City Planning, Housing Project-Level Database](https://www.nyc.gov/content/planning/pages/resources/datasets/housing-project-level#overview)

**Purpose and Use:**
This dataset serves as the **primary source for demolition activity** in New York City. It will be filtered to isolate **completed residential demolitions** and categorized by ownership type in order to distinguish between:

* **Government / Non-Profit ownership**, used as a proxy for affordable or subsidized housing, and
* **Private ownership**, used as a proxy for non-subsidized housing.

The cleaned demolition data will be aggregated by time (monthly) and used as an explanatory variable in downstream analysis, including time-series modeling and comparisons with homelessness trends.

**Size:**

* **Rows:** Approximately 70,000 total rows in the full dataset (varies depending on years selected). This includes both construction and demolition records, across residential and non-residential projects.
* **Columns:** 63 total columns.

**Key Variables Used:**

* **Job Type:** Filtered to `Demolition`
* **ResIDFlag:** Filtered to residential projects only
* **NonresIDFlag:** Must be empty (to exclude non-residential projects)
* **Job_Status:** Filtered to `Completed`
* **Ownership:** Used to classify projects as `Government/Non-Profit` or `Private`
* **Date Completed:** Date the demolition was completed; used for time-based aggregation and joining

**Aggregation Level:**

* Not aggregated; project-level data.



## Data Source 2: NYC Department of Homeless Services (DHS) – Data Dashboard

**Source:**
[NYC Department of Homeless Services, DHS Data Dashboard](https://data.cityofnewyork.us/Social-Services/DHS-Data-Dashboard/5e9h-x6ak/about_data)

**Purpose and Use:**
This dataset provides **monthly homelessness trends** and is used to evaluate whether changes in shelter populations align with demolition activity over time. It supports validation of the project’s central research question by identifying patterns and shifts in the number of individuals experiencing homelessness.

**Size:**

* **Rows:** 121 rows
* **Temporal Coverage:** Multiple years of data aggregated by month
* **Columns:** 58 columns

**Key Variables Used:**

* **FWC Unique Individuals by Age – Total:** Primary outcome variable representing the total number of unique individuals in shelters
* **Reporting Date:** Monthly reporting date used for time-series analysis and dataset joining

**Aggregation Level:**

* Aggregated at the **monthly** level.



## Data Integration and Modeling Approach

**Join Strategy:**
The DCP Housing data and DHS homelessness data will be joined on **date fields**, after aggregating demolition counts to a monthly level to align with the DHS reporting cadence.

**Analytical Use:**

* Monthly counts of residential demolitions (with a focus on government and non-profit ownership) will be incorporated as exogenous variables.
* These variables will be used in a **SARIMAX / ARIMAX time-series model** to evaluate whether demolition activity helps explain or predict changes in the number of unique individuals in NYC homeless shelters over time.

This integrated approach allows the analysis to move beyond descriptive trends and toward modeling potential structural relationships between housing loss and homelessness.

##  Data Limitations & Assumptions
| Data Source Name | Potential Limitation(s) / Assumption(s) | Potential Impact on Analysis |
|------------------|------------------------------------------|------------------------------|
| Affordable Housing Pages <br> Housing Connect (HPD, HDC) <br> Housing - MOPD <br> HUD <br> NYCHA | We are assuming some of the ownership (column in DCP) of agencies listed in our DCP Housing Database are part of our affordable/government subsidized category.|Assumptions: For our analysis, we must assume that ownership by these agencies mentioned on this web page are included in the “affordable” category due to government subsidizing/lower rent. | |
| DCP (Department of City Planning) HOUSING DATABASE | We are using the latest release of the DCP Housing Database, which includes years from 2019-2021 | Assumptions: We are to assume COVID had an impact, but not drastic enough to affect our analysis. | |


### Data Attribution and Licensing

This project uses publicly available datasets provided by New York City agencies through NYC Open Data and official agency websites. All data are used in accordance with the NYC Open Data Terms of Use.

**Data Sources:**
- **NYC Department of City Planning (DCP) – Housing Database**  
  [NYC Department of City Planning, Housing Project-Level Database](https://www.nyc.gov/content/planning/pages/resources/datasets/housing-project-level#overview)
  <br>License: NYC Open Data Terms of Use (Open Data)

- **NYC Department of Homeless Services (DHS) – Data Dashboard**  
  [NYC Department of Homeless Services, DHS Data Dashboard](https://data.cityofnewyork.us/Social-Services/DHS-Data-Dashboard/5e9h-x6ak/about_data) 
  <br>License: NYC Open Data Terms of Use (Open Data)

- **Affordable Housing Reference Pages**  
  Sources include Housing Connect (HPD/HDC), MOPD, HUD, and NYCHA official websites.  
  These sources are used for contextual classification and ownership assumptions only.

All datasets remain the property of their respective agencies. This project is for educational and analytical purposes and does not claim ownership over the source data.




