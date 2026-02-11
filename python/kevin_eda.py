import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

conn = sqlite3.connect('/Users/Marcy_Student/Desktop/CID_FINAL/TeamHousing/data/processed/nyc_demolitions.db')
cursor = conn.cursor()

query = """
SELECT *
FROM fact_demolitions f   
"""

fact_owner_demo = pd.read_sql_query(query, conn)

# Filter to Affordable housing only
affordable_only = fact_owner_demo[
    fact_owner_demo['ownership_id'] != 1
]

# Count total affordable jobs
total_affordable = len(affordable_only)

# Count affordable demolitions
affordable_demolished = affordable_only[
    affordable_only['job_typeid'] == 2
]

num_affordable_demolished = len(affordable_demolished)

# Percentage
pct_affordable_demolished = num_affordable_demolished / total_affordable

print(f"Total Affordable jobs: {total_affordable}")
print(f"Affordable demolitions: {num_affordable_demolished}")
print(f"Percent of Affordable housing demolished: {pct_affordable_demolished:.2%}")

# Filter to Affordable housing only
private_only = fact_owner_demo[
    fact_owner_demo['ownership_id'] == 1
]

# Count total affordable jobs
total_private = len(private_only)

# Count affordable demolitions
private_demolished = private_only[
    private_only['job_typeid'] == 2
]

num_private_demolished = len(private_demolished)

# Percentage
pct_private_demolished = (num_private_demolished / total_private) 

print(f"Total Private jobs: {total_private}")
print(f"Private demolitions: {num_private_demolished}")
print(f"Percent of Private housing demolished: {pct_private_demolished:.2%}")

fact_owner_demo['is_demolition'] = fact_owner_demo['job_typeid'] == 2
fact_owner_demo['is_private'] = fact_owner_demo['ownership_id'] == 1

affordable_by_borough = (
    fact_owner_demo[fact_owner_demo['is_private'] == False]
    .groupby('borough')
    .agg(
        total_affordable_jobs=('job_number', 'count'),
        affordable_demolitions=('is_demolition', 'sum')
    )
)

affordable_by_borough['pct_affordable_demolished'] = (
    (affordable_by_borough['affordable_demolitions'] /
    affordable_by_borough['total_affordable_jobs']) * 100
)

private_by_borough = (
    fact_owner_demo[fact_owner_demo['is_private'] == True]
    .groupby('borough')
    .agg(
        total_private_jobs=('job_number', 'count'),
        private_demolitions=('is_demolition', 'sum')
    )
)

private_by_borough['pct_private_demolished'] = (
    (private_by_borough['private_demolitions'] /
    private_by_borough['total_private_jobs']) * 100
)

borough_summary = (
    affordable_by_borough
    .merge(private_by_borough, left_index=True, right_index=True, how='outer')
)

print(borough_summary)

# # Count demolitions by borough and ownership type
# demo_counts = (
#     fact_owner_demo
#     .groupby(['borough', 'ownership_type','job_type'])
#     .size()
#     .reset_index(name='num_demolitions')
# )

# print(demo_counts)

# demo_pivot = (
#     fact_owner_demo
#     .groupby(['borough', 'ownership_type','job_type'])
#     .size()
#     .unstack(fill_value=0)
# )

# demo_pivot['Total'] = demo_pivot.sum(axis=1)
# demo_pivot['Private_pct'] = demo_pivot['Private'] / demo_pivot['Total']
# demo_pivot['Affordable_pct'] = demo_pivot['Affordable'] / demo_pivot['Total']

# print(demo_pivot)



# job_By_Borough = (fact_owner_demo.groupby(['borough','private'])['job_number'].count()
#                   .reset_index()
#                   .sort_values(by='job_number', ascending=True))

# # plot showing number of demolitions by borough and ownership type
# sns.barplot(
#     data=job_By_Borough, 
#     x='borough', 
#     y='job_number', 
#     hue='private'
# )

# plt.title('Job Numbers by Borough and Ownership Category')
# plt.xlabel('Borough')
# plt.ylabel('Count of Job Numbers')
# plt.legend(title='Ownership Type')

# plt.xticks(rotation=45)

# plt.show()