import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/data/processed/nyc_demolitions.db"

conn = sqlite3.connect(DB_PATH)
fact = pd.read_sql_query("SELECT * FROM fact_demolitions", conn)
dim_owner = pd.read_sql_query("SELECT * FROM dim_ownership", conn)
shelters = pd.read_sql_query("SELECT * FROM fact_shelters", conn)

conn.close()

df = fact.merge(dim_owner, on="ownership_id", how="left")

df["month_date"] = pd.to_datetime(df["month_date"])
df["year"] = df["month_date"].dt.year

shelters["report_date"] = pd.to_datetime(shelters["report_date"])
shelters["year"] = shelters["report_date"].dt.year



# Combine Government + Non-Profit into Affordable
df["ownership_group"] = df["ownership_clean"].replace({
    "Government": 1,
    "Private Non-Profit": 1,
    "Private For-Profit": 2
})

df_filtered = df[(df["year"]>=2023) & (df['job_typeid'] == 1)]
shelter_demo_filtered = shelters[shelters['year']>=2023]

# affordable demolitions only
affordable_demo = df_filtered[
    df_filtered["ownership_group"] == 1
]

# count demolitions by year
demo_yearly = (
    affordable_demo
    .groupby("year")
    .size()
    .reset_index(name="affordable_demolitions")
)

# average shelter count by year
shelter_yearly = (
    shelter_demo_filtered
    .groupby("year")["shelter_count"]
    .mean()
    .reset_index()
)

print(demo_yearly)
print(shelter_yearly)


fig, ax1 = plt.subplots()

# demolitions
ax1.plot(
    demo_yearly["year"],
    demo_yearly["affordable_demolitions"],
    label="Affordable Demolitions",
    marker="o"
)

ax1.set_ylabel("Affordable Demolitions")

# second axis for shelters (different scale)
ax2 = ax1.twinx()

ax2.plot(
    shelter_yearly["year"],
    shelter_yearly["shelter_count"],
    label="Shelter Count",
    linestyle="--",
    marker="o"
)

ax2.set_ylabel("Shelter Count")

plt.title("Affordable Demolitions vs Shelter Counts (2023+)")

fig.tight_layout()

plt.show()