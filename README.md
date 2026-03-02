# Open Door Plan 
## By team: Keys to the City 

## Executive Summary
This project investigates whether demolition of government and non-profit owned residential buildings — used as a proxy for affordable housing — is predictive of changes in New York City’s shelter population from 2016 to 2022.
Using publicly available NYC government datasets, we:
- Built a cleaned relational database
- Conducted statistical testing on demolition patterns
- Engineered monthly time-series features
- Implemented SARIMAX forecasting models
- Evaluated model performance using AIC, BIC, and RMSE

While affordable demolitions occur at statistically significant rates, our results indicate they do not meaningfully predict shelter population fluctuations at the citywide monthly level.
Instead, shelter population dynamics appear to be driven primarily by macro-level shocks and policy interventions — particularly during COVID-19 and post-2022 migration inflows.
This project demonstrates both the value and the limitations of system-level administrative data when studying housing displacement and homelessness.

## Critical Research Question (CRQ)
Using government and non-profit owned housing as a proxy for affordability, is variation in the monthly counts of demolition job records predictive of changes in New York City’s shelter population over time, accounting for seasonality, from 2015 to 2024?
## Hypothesis  
We hypothesize that higher monthly counts of public housing demolition job records will be predictive of increases in the NYC shelter population, potentially with a lag of several months.


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
- **[NYC Department of City Planning, Housing Project-Level Database](https://www.nyc.gov/content/planning/pages/resources/datasets/housing-project-level#overview)
  <br>License: NYC Open Data Terms of Use (Open Data)**

- **[NYC Department of Homeless Services, DHS Data Dashboard](https://data.cityofnewyork.us/Social-Services/DHS-Data-Dashboard/5e9h-x6ak/about_data) 
  <br>License: NYC Open Data Terms of Use (Open Data)**

- **Affordable Housing Reference Pages**  
  Sources include Housing Connect (HPD/HDC), MOPD, HUD, and NYCHA official websites.  
  These sources are used for contextual classification and ownership assumptions only.

All datasets remain the property of their respective agencies. This project is for educational and analytical purposes and does not claim ownership over the source 

## Key Data Processing Decisions

* Filtered to completed residential demolitions only
* Classified ownership as Government/Non-Profit vs Private
* Used ownership as an affordability proxy
* Aggregated demolition counts to monthly level
* Joined datasets on month-year
* Standardized date formatting for stationarity
* Built a SQLite relational database to improve query efficiency

A structured analytical workflow was used:

1. Describe observable trends
2. Test statistically
3. Model and evaluate predictive power

## Exploratory Findings

## Average Shelter Counts by Year (2016–2023)

<img width="701" height="661" alt="avg_shelter_countByYear" src="https://github.com/user-attachments/assets/b03125d7-f9c1-49c5-82ef-6df62b87e270" />

**Figure 1.** Annual average shelter population trends in New York City from 2016 through 2023.

### Shelter Population Trends (2016–2022)

* Gradual decline from 2016–2019
* Sharp drop during 2020–2021 (COVID period)
* Significant rebound beginning 2022

The COVID-era decline likely reflects:

* Emergency rehousing programs
* Reduced intake policies
* Shelter capacity constraints
* Rental assistance expansion

This suggests that **Shelter_Count reflects policy capacity decisions, not just homelessness demand.**

### Demolition & Construction Trends

* Construction activity spikes in 2019
* Sharp construction decline in 2020
* Demolitions remain relatively stable across years

Supply additions appear cyclical, while demolitions are structurally persistent.

## Statistical Testing

A two-proportion Z-test was conducted to compare demolition rates of:

* Government/Non-Profit buildings
* Private buildings

Results show a statistically significant difference (p < 0.05), with affordable proxy buildings demolished at higher proportional rates.

This supports evidence of redevelopment pressure on publicly owned housing stock.

However, statistical significance does not imply meaningful predictive impact, which becomes clear in modeling results.


## Time-Series Modeling

We implemented a SARIMAX framework to forecast shelter population trends.

### Dependent Variable

* Monthly Unique Individuals in Shelter

### Exogenous Variables

* Affordable demolition counts
* Total demolition counts
* Seasonal components
* COVID intervention dummy

## Stationarity & Structural Break

Initial diagnostics revealed non-stationarity driven by COVID-19 disruptions.

To address this:

* Differencing was applied
* A COVID structural intervention variable was introduced

This improved convergence and information criteria but did not significantly increase demolition variable explanatory power.


## Model Performance Metrics

Several model specifications were evaluated.

### Baseline Model

* RMSE: 1,599.587

### ARIMA (1,0,1)

* RMSE: 6,581.286
* AIC: 1100.482
* BIC: 1109.301

### Seasonal SARIMA (1,0,0)(1,0,0,12)

* RMSE: 11,004.713
* AIC: 1084.994
* BIC: 1091.608

### Seasonal SARIMAX (1,0,0)(1,1,0,12)

* RMSE: 5,685.164
* AIC: 726.855
* BIC: 733.806

The seasonal SARIMAX model substantially improved information criteria relative to simpler models, indicating better structural fit after accounting for seasonality and COVID intervention effects.

However, demolition variables contributed limited predictive improvement.


## Key Modeling Insight

Affordable demolitions showed minimal explanatory contribution to shelter population forecasts.

Residual analysis revealed divergence periods where approximately **16,000 individuals remained unexplained** by demolition trends alone.

Shelter population variation was primarily explained by:

* Autoregressive dynamics
* Seasonal variation
* COVID structural intervention effects

This suggests demolition activity does not meaningfully forecast citywide shelter population at the monthly level.

## Why the Model Underperforms

### Shelter Count ≠ Total Homelessness

Shelter population is influenced by:

* Capacity policies
* Intake restrictions
* Prevention programs
* Emergency housing expansion
* Migration flows

COVID-era shocks reflect policy responses rather than pure demand shifts.

### System-Level Aggregation

This study operates at citywide monthly aggregation. It cannot:

* Track individual displacement
* Observe neighborhood-level effects
* Measure length-of-stay
* Capture unsheltered populations

### Affordability Proxy Limitations

Government/non-profit ownership is an imperfect proxy:

* Not all government units are deeply affordable
* Some private developments contain subsidized units
* Unit-level affordability data is not directly observed

## Policy Implications

Housing development trends suggest supply expansion efforts are underway.

However, this analysis demonstrates:

Shelter occupancy data alone cannot capture displacement effects resulting from affordable housing demolitions.

Improved measurement systems are necessary to evaluate redevelopment impacts on vulnerable populations.

## Recommendations

**Improve Housing Impact Measurement**
Require unit-level reporting and transparent one-for-one replacement accounting.

**Expand Homelessness Measurement**
Incorporate unsheltered counts, eviction filings, rental assistance utilization, and length-of-stay data.

**Require Net Positive Affordable Unit Growth**
Condition redevelopment approvals on net increases in affordable units rather than replacement alone.

**Strengthen Transitional Displacement Protections**
Expand relocation assistance and right-to-return guarantees to reduce short-term shelter system strain.


## 2022–Present Context

Shelter population increased sharply beginning in 2022 and surged further in 2023.

These trends align with:

* Migration inflows
* Expiration of pandemic housing protections
* Tight rental market conditions

This reinforces that macroeconomic and migration shocks play a larger role in shelter population shifts than demolition activity alone.


## Final Conclusion

Affordable housing demolitions occur at statistically significant rates.

However, they do not meaningfully predict shelter population changes at the citywide monthly level.

Shelter counts are heavily influenced by policy design and macro-level shocks. Current administrative data restricts analysis to system-level relationships rather than individual displacement pathways.

This project highlights both the analytical value and structural limits of time-series forecasting in evaluating housing policy impacts.

## Interactive Tableau Dashboard

Explore our full interactive visualization and analysis dashboard below:

🔗 **[Open Door Plan — NYC Housing & Homelessness Dashboard (Tableau Public)](https://public.tableau.com/app/profile/kevin.serrano6220/viz/Dashboard_17718985977530/Dashboard1?publish=yes)**

This dashboard provides interactive visualizations of shelter population trends, demolition activity, construction patterns, and key exploratory findings used throughout this analysis.

<img width="1420" height="800" alt="Screenshot 2026-03-01 at 11 42 46 PM" src="https://github.com/user-attachments/assets/9df5c1b6-26ef-4eb6-92ea-01e898fc64be" />





## 👥 Project Team

Meet the team behind this project and their core technical contributions.

---

<table>
<tr>

<td align="center" width="33%">

### 👨🏻‍💻 Vincent Perez  
**Project Manager**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/thevinceperez/)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/vrpperez7)

**Contributions**
- Database Schema Design
- Database Development & Implementation
- Model Training

</td>

<td align="center" width="33%">

### 📊 Thomas Segal  
**Data Analyst**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/thomas-segal-093370369/)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/Commit-Thomas)

**Contributions**
- Data Cleaning, Filtering and Validation
- Hypothesis Testing
- Statistical Analysis

</td>

<td align="center" width="33%">

### 📈 Kevin Serrano Lopez  
**Data Analyst & Visualization**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/kevin-serrano-lopez/)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/kevinserr)

**Contributions**
- Data Validation
- Exploratory Data Analysis (EDA)
- Dashboard Development

</td>

</tr>
</table>


