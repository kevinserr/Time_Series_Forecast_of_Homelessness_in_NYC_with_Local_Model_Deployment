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
WHERE f.job_typeid == 2 
"""

fact_owner_demo = pd.read_sql_query(query, conn)

job_By_Borough = (fact_owner_demo.groupby(['borough', 'ownership_id'])['job_number']
                  .count()
                  .reset_index()
                  .sort_values(by='job_number', ascending=True))

# plot showing number of demolitions by borough and ownership type
sns.barplot(
    data=job_By_Borough, 
    x='borough', 
    y='job_number', 
    hue='ownership_id'
)

plt.title('Job Numbers by Borough and Ownership Category')
plt.xlabel('Borough')
plt.ylabel('Count of Job Numbers')
plt.legend(title='Ownership Type')

plt.xticks(rotation=45)

plt.show()