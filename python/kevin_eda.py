import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/data/processed/nyc_demolitions.db"

conn = sqlite3.connect(DB_PATH)

fact = pd.read_sql_query("SELECT * FROM fact_demolitions", conn)
dim_owner = pd.read_sql_query("SELECT * FROM dim_ownership", conn)
shelters = pd.read_sql_query("SELECT * FROM fact_shelters", conn)

conn.close()

# prepare demolition data

df = fact.merge(dim_owner, on="ownership_id", how="left")

df["month_date"] = pd.to_datetime(df["month_date"])
df["year"] = df["month_date"].dt.year

# Combine Government + Non-Profit into Affordable
df["ownership_group"] = df["ownership_clean"].replace({
    "Government": "Affordable",
    "Private Non-Profit": "Affordable",
    "Private For-Profit": "Private For-Profit"
})


# overall percentage share

overall_counts = df["ownership_group"].value_counts()
overall_percent = overall_counts / overall_counts.sum() * 100

print("\nOverall % of Demolitions")
print(overall_percent)


# percentage share by year

yearly_counts = df.groupby(["year", "ownership_group"]).size().unstack()
yearly_percent = yearly_counts.div(yearly_counts.sum(axis=1), axis=0) * 100

print("\nYearly % of Demolitions")
print(yearly_percent)


# preparing shelter data

shelters["report_date"] = pd.to_datetime(shelters["report_date"])
shelters["year"] = shelters["report_date"].dt.year

yearly_shelter = shelters.groupby("year")["shelter_count"].mean()


# merge to compare 

affordable_counts = yearly_counts["Affordable"]

comparison = pd.concat(
    [affordable_counts, yearly_shelter],
    axis=1
)

comparison.columns = [
    "Affordable_Demolition_Count",
    "Avg_Shelter_Count"
]

print("\nCombined Dataset")
print(comparison)


# corr analysis

# Levels correlation
corr_levels = comparison.corr().iloc[0, 1]
print(f"\nCorrelation (Levels): {corr_levels:.3f}")

# Year-over-year changes
comparison["Affordable_YoY_Change"] = comparison["Affordable_Demolition_Count"].diff()
comparison["Shelter_YoY_Change"] = comparison["Avg_Shelter_Count"].diff()

corr_diff = comparison[
    ["Affordable_YoY_Change", "Shelter_YoY_Change"]
].corr().iloc[0, 1]

print(f"Correlation (Year-over-Year Changes): {corr_diff:.3f}")



# plot

# Plot 1: Yearly % Share
plt.figure()
yearly_percent.plot()
plt.title("Yearly % of Demolitions: Private vs Affordable")
plt.xlabel("Year")
plt.ylabel("Percent")
#plt.show()

# Plot 2: Affordable Demolition Count
plt.figure()
comparison["Affordable_Demolition_Count"].plot()
plt.title("Affordable Demolitions (Absolute Count)")
plt.xlabel("Year")
plt.ylabel("Count")
#plt.show()

# Plot 3: Shelter Population
plt.figure()
comparison["Avg_Shelter_Count"].plot()
plt.title("Average Annual Shelter Population")
plt.xlabel("Year")
plt.ylabel("Shelter Count")


# Borough Analysis

# Borough-Year Counts
borough_year_counts = (
    df.groupby(["borough", "year", "ownership_group"])
      .size()
      .unstack()
      .fillna(0)
)

# Borough-Year Percentage Share (Affordable)
borough_year_percent = borough_year_counts.div(
    borough_year_counts.sum(axis=1),
    axis=0
) * 100

borough_affordable_pct = borough_year_percent["Affordable"].unstack("borough")

print("\nBorough-Year Affordable")
print(borough_affordable_pct)

# Plot 1: Borough Affordable 

plt.figure()
borough_affordable_pct.plot()
plt.title("Affordable Demolition % by Borough")
plt.xlabel("Year")
plt.ylabel("Percent")
plt.tight_layout()




# Plot 2: Total Demolitions by Borough

borough_total = (
    df.groupby(["borough", "year"])
      .size()
      .unstack("borough")
)

plt.figure()
borough_total.plot()
plt.title("Total Demolitions by Borough")
plt.xlabel("Year")
plt.ylabel("Count")
plt.tight_layout()
plt.close()



# Demolitions vs New Buildings 
# By Year + Ownership Type


# Label job types
df["job_type"] = df["job_typeid"].replace({
    1: "New Building",
    2: "Demolition"
})


# Yearly Counts by Job Type

year_job_counts = (
    df.groupby(["year", "job_type"])
      .size()
      .unstack()
      .fillna(0)
)

print("\nYearly Demolitions vs New Buildings")
print(year_job_counts)

# Proportion of demolitions vs new buildings per year
year_job_percent = year_job_counts.div(
    year_job_counts.sum(axis=1),
    axis=0
) * 100

print("\nYearly % Demolition vs New Building")
print(year_job_percent)

#Year + Ownership + Job Type
year_owner_job = (
    df.groupby(["year", "ownership_group", "job_type"])
      .size()
      .unstack()
      .fillna(0)
)

print("\n=== Year + Ownership + Job Type Counts ===")
print(year_owner_job)

# Yearly construction vs demolition
# Citywide Counts by Year
year_counts = (
    df.groupby(["year", "job_type"])
      .size()
      .unstack()
      .fillna(0)
)

year_counts["Net_Difference"] = (
    year_counts["New Building"] -
    year_counts["Demolition"]
)

print("\nCitywide Construction vs Demolition")
print(year_counts)

# Ownership-Level Counts by Year

year_owner_counts = (
    df.groupby(["year", "ownership_group", "job_type"])
      .size()
      .unstack()
      .fillna(0)
)

year_owner_counts["Net_Difference"] = (
    year_owner_counts["New Building"] -
    year_owner_counts["Demolition"]
)

print("\nConstruction vs Demolition by Ownership")
print(year_owner_counts)

# Plot Citywide Counts
plt.figure()
year_counts["New Building"].plot(label="New Building")
year_counts["Demolition"].plot(label="Demolition")
plt.title("Citywide Construction vs Demolition")
plt.xlabel("Year")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.savefig("/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/graphs/citywide_construction_vs_demolition.png", dpi=300)
plt.close()


# Plot Net Difference (Citywide)


plt.figure()
year_counts["Net_Difference"].plot()
plt.axhline(0)
plt.title("Citywide Net Difference (New - Demo)")
plt.xlabel("Year")
plt.ylabel("Net Difference")
plt.tight_layout()
plt.savefig("/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/graphs/citywide_net_difference.png", dpi=300)
plt.close()


# Plot Net Difference by Ownership
affordable_net = (
    year_owner_counts
        .xs("Affordable", level=1)["Net_Difference"]
)

private_net = (
    year_owner_counts
        .xs("Private For-Profit", level=1)["Net_Difference"]
)

plt.figure()
affordable_net.plot(label="Affordable")
private_net.plot(label="Private For-Profit")
plt.axhline(0)
plt.title("Net Difference by Ownership (New - Demo)")
plt.xlabel("Year")
plt.ylabel("Net Difference")
plt.legend()
plt.tight_layout()
plt.savefig("/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/graphs/net_difference_by_ownership.png", dpi=300)
plt.close()


print("\nConstruction vs Demolition analysis complete.")

# Affordable net vs shelter


# Compute Affordable Net Difference by Year
affordable_year = (
    df[df["ownership_group"] == "Affordable"]
      .groupby(["year", "job_type"])
      .size()
      .unstack()
      .fillna(0)
)

affordable_year["Net_Difference"] = (
    affordable_year["New Building"] -
    affordable_year["Demolition"]
)

print("\nAffordable Net Difference by Year")
print(affordable_year)


# Merge with Shelter Data


affordable_vs_shelter = pd.concat(
    [affordable_year["Net_Difference"], yearly_shelter],
    axis=1
)

affordable_vs_shelter.columns = [
    "Affordable_Net_Difference",
    "Avg_Shelter_Count"
]

print("\nAffordable Net vs Shelter")
print(affordable_vs_shelter)


# Correlation (Levels)
corr_levels = affordable_vs_shelter.corr().iloc[0, 1]
print(f"\nCorrelation (Levels): {corr_levels:.3f}")

# Correlation (Year-over-Year Changes)

affordable_vs_shelter["Net_YoY_Change"] = (
    affordable_vs_shelter["Affordable_Net_Difference"].diff()
)

affordable_vs_shelter["Shelter_YoY_Change"] = (
    affordable_vs_shelter["Avg_Shelter_Count"].diff()
)

corr_diff = affordable_vs_shelter[
    ["Net_YoY_Change", "Shelter_YoY_Change"]
].corr().iloc[0, 1]

print(f"Correlation (Year-over-Year Changes): {corr_diff:.3f}")

# AFFORDABLE NEW BUILDINGS vs SHELTER



# Affordable New Building Counts by Year


affordable_new = (
    df[
        (df["ownership_group"] == "Affordable") &
        (df["job_type"] == "New Building")
    ]
    .groupby("year")
    .size()
)

print("\nAffordable New Buildings by Year")
print(affordable_new)

# merge with shelter data

affordable_new_vs_shelter = pd.concat(
    [affordable_new, yearly_shelter],
    axis=1
)

affordable_new_vs_shelter.columns = [
    "Affordable_New_Buildings",
    "Avg_Shelter_Count"
]

print("\nAffordable New Buildings vs Shelter")
print(affordable_new_vs_shelter)


# corr levels 
corr_levels = affordable_new_vs_shelter.corr().iloc[0, 1]
print(f"\nCorrelation (Levels): {corr_levels:.3f}")


# corr year to year
affordable_new_vs_shelter["New_YoY_Change"] = (
    affordable_new_vs_shelter["Affordable_New_Buildings"].diff()
)

affordable_new_vs_shelter["Shelter_YoY_Change"] = (
    affordable_new_vs_shelter["Avg_Shelter_Count"].diff()
)

corr_diff = affordable_new_vs_shelter[
    ["New_YoY_Change", "Shelter_YoY_Change"]
].corr().iloc[0, 1]

print(f"Correlation (Year-over-Year Changes): {corr_diff:.3f}")

import statsmodels.api as sm


# affordable demolitions
affordable_demo = (
    df[
        (df["ownership_group"] == "Affordable") &
        (df["job_type"] == "Demolition")
    ]
    .groupby("year")
    .size()
)

# private demolitions
private_demo = (
    df[
        (df["ownership_group"] == "Private For-Profit") &
        (df["job_type"] == "Demolition")
    ]
    .groupby("year")
    .size()
)

# combine dataset
model_df = pd.concat(
    [affordable_demo, private_demo, yearly_shelter],
    axis=1
).dropna()

model_df.columns = [
    "Affordable_Demo",
    "Private_Demo",
    "Shelter_Count"
]

model_df = model_df.sort_index()


# lag variables
model_df["Affordable_Lag1"] = model_df["Affordable_Demo"].shift(1)
model_df["Private_Lag1"] = model_df["Private_Demo"].shift(1)

# first differences
model_df["Affordable_Change"] = model_df["Affordable_Demo"].diff()
model_df["Private_Change"] = model_df["Private_Demo"].diff()
model_df["Shelter_Change"] = model_df["Shelter_Count"].diff()


# ------------------------
# model 1 baseline
# ------------------------

baseline = model_df.dropna()

X1 = sm.add_constant(
    baseline[["Affordable_Demo","Private_Demo"]]
)

y1 = baseline["Shelter_Count"]

model1 = sm.OLS(y1, X1).fit()

print("\nbaseline model")
print(model1.summary())


# ------------------------
# model 2 lagged
# ------------------------

lag_df = model_df.dropna()

X2 = sm.add_constant(
    lag_df[["Affordable_Lag1","Private_Lag1"]]
)

y2 = lag_df["Shelter_Count"]

model2 = sm.OLS(y2, X2).fit()

print("\nlagged model")
print(model2.summary())


# ------------------------
# model 3 change model
# ------------------------

change_df = model_df.dropna()

X3 = sm.add_constant(
    change_df[["Affordable_Change","Private_Change"]]
)

y3 = change_df["Shelter_Change"]

model3 = sm.OLS(y3, X3).fit()

print("\nchange model")
print(model3.summary())


# ------------------------
# export regression tables
# ------------------------

results = pd.DataFrame({

"baseline_coef":model1.params,
"baseline_p":model1.pvalues,

"lag_coef":model2.params,
"lag_p":model2.pvalues,

"change_coef":model3.params,
"change_p":model3.pvalues

})

results.to_csv("regression_results.csv")


# ------------------------
# fitted vs actual plot
# ------------------------

model_df["Fitted_Lag_Model"] = model2.predict(
    sm.add_constant(
        model_df[["Affordable_Lag1","Private_Lag1"]]
    )
)

plt.figure()

model_df["Shelter_Count"].plot(label="Actual Shelter Count")

model_df["Fitted_Lag_Model"].plot(
    label="Fitted (Lag Model)"
)

plt.title("Shelter Counts vs Demolition Model Fit")

plt.xlabel("Year")

plt.ylabel("Shelter Count")

plt.legend()

plt.tight_layout()

plt.savefig(
    "shelter_vs_demolition_model_fit.png",
    dpi=300
)

plt.close()


# ------------------------
# R2 comparison export
# ------------------------

model_compare = pd.DataFrame({

"Model":[
"Baseline",
"Lagged",
"Change"
],

"R_squared":[
model1.rsquared,
model2.rsquared,
model3.rsquared
],

"Adj_R_squared":[
model1.rsquared_adj,
model2.rsquared_adj,
model3.rsquared_adj
]

})

model_compare.to_csv("model_comparison.csv",index=False)

print("\nmodels completed")


