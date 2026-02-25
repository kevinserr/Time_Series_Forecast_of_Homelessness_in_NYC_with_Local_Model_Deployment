"""
NYC HOUSING DEMOLITIONS + SHELTER ANALYSIS (EDA SCRIPT)

PURPOSE
This script performs exploratory data analysis (EDA) on NYC housing
demolitions and shelter usage to investigate relationships between:
1. Ownership type (Affordable vs For-Profit)
2. Demolition activity over time
3. Shelter population trends
4. COVID-19 shock period impacts

DATA SOURCES
Database: nyc_demolitions.db

Tables Used:
- fact_demolitions : demolition and construction job records
- dim_ownership    : ownership classification lookup table
- fact_shelters    : NYC shelter reporting records

WORKFLOW OVERVIEW:
1. Connect to SQLite database and load required tables.
2. Merge demolition facts with ownership classifications.
3. Engineer datetime variables for time-based analysis.
4. Create ownership group categories:
      Government + Non-Profit → Affordable
      Private For-Profit → For-Profit
5. Label job types (Construction vs Demolition).
6. Filter analysis period (2016–2022).
7. Create COVID dummy variables (March 2020 — Dec 2021)
   for use as exogenous model controls.
8. Generate demolition indicators for hypothesis testing.
9. Perform Proportion Z-Test:
      Test whether Affordable housing experiences a higher
      demolition rate than For-Profit housing.
10. Produce time-series visualizations:
      - Monthly demolition trends
      - Shelter reporting trends

OUTPUTS
- Statistical hypothesis test results.
- Monthly demolition time series plots.
- Shelter count trend plots.

NOTES
COVID period chosen based on NYC operational disruptions
beginning March 2020 through late recovery phase in 2021.
"""
# imports
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportions_ztest
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# database connections
DB_PATH = "/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/data/processed/nyc_demolitions.db"

conn = sqlite3.connect(DB_PATH)

# load data
fact_demo = pd.read_sql_query(
    "SELECT * FROM fact_demolitions",
    conn
)

dim_owner = pd.read_sql_query(
    "SELECT * FROM dim_ownership",
    conn
)

fact_shelters = pd.read_sql_query(
    "SELECT * FROM fact_shelters",
    conn
)

conn.close()


# merge demolition facts and demolition owner type
df = fact_demo.merge(
    dim_owner,
    on="ownership_id",
    how="left"
)

# Date Engineering
df["month_date"] = pd.to_datetime(df["month_date"])
df["year"] = df["month_date"].dt.year

fact_shelters["report_date"] = pd.to_datetime(
    fact_shelters["report_date"]
)
fact_shelters["year"] = (
    fact_shelters["report_date"].dt.year
)

# Ownership Groups
# Affordable = Government + Non-Profit
df["ownership_group"] = df["ownership_clean"].replace({
    "Government": "Affordable",
    "Private Non-Profit": "Affordable",
    "Private For-Profit": "For-Profit"
})


# Job Type Labels
job_map = {
    1: "construction",
    2: "demolition"
}
df["job_type"] = df["job_typeid"].map(job_map)

# Time Filtering
# 2016 - 2023
df = df[(df["year"] >= 2016) & (df["year"] < 2023)] 
fact_shelters = fact_shelters[(fact_shelters["year"] >= 2016)
                              & (fact_shelters["year"] < 2023)]

# checking for weeks where covid affect shelter counts
# for model exog var
fact_shelters['covid_dummy'] = 0
fact_shelters.loc[
    (fact_shelters['report_date'] >= '2020-03-01') &
    (fact_shelters['report_date'] <= '2021-12-01'),
    'covid_dummy'
] = 1

# Affordable vs For-Profit
# Demolition Indicator
df["is_demolition"] = (
    df["job_typeid"] == 2
).astype(int)

df["is_affordable"] = (
    df["ownership_group"] == "Affordable"
).astype(int)

# added dummy var to signify covid impact in our demolition dataset 
df['covid_dummy'] = 0
df.loc[
    (df['month_date'] >= '2020-03-01') &
    (df['month_date'] <= '2021-12-01'),
    'covid_dummy'
] = 1

# Proportion Z-Test
# (Thomas Analysis)
affordable = df[df["is_affordable"] == 1]
forprofit = df[df["is_affordable"] == 0]

count = np.array([
    affordable["is_demolition"].sum(),
    forprofit["is_demolition"].sum()
])

nobs = np.array([
    len(affordable),
    len(forprofit)
])

if np.any(nobs == 0):
    print("Error: One group has zero observations.")
else:

    stat, pval = proportions_ztest(
        count,
        nobs,
        alternative='larger'
    )

    print("\nZ-Test Results")
    print("----------------")
    print("Z Statistic:", stat)
    print("P Value:", pval)

# Monthly Demolition Trend
monthly_demo = (
    df[df["job_type"] == "demolition"]
    .groupby("month_date")
    .size()
)

plt.figure()

monthly_demo.plot()

plt.title("Monthly Demolitions Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Demolitions")

# Shelter Counts Over Time
monthly_shelter = (
    fact_shelters
    .set_index("report_date")
    .resample("M")["shelter_count"]
    .sum()
)

plt.figure(figsize=(12,6))

plt.plot(monthly_shelter)

plt.title("Shelter Counts Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Shelter Records")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()