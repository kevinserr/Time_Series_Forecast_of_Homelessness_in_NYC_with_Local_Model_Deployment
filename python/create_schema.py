# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# PATH TO DEMOLITION AND HOMELESS DATA (add to your own path)
demolition_path = "/Users/beans/Desktop/TeamHousing/data/HousingDB_post2010.csv"
homeless_path = "/Users/beans/Desktop/TeamHousing/data/DHS_Data_Dashboard.csv"

demo_raw=pd.read_csv(demolition_path)
homeless_raw=pd.read_csv(homeless_path)


# %%
homeless_raw['Report Date'] = pd.to_datetime(
    homeless_raw['Report Date'],
    errors='coerce'
)

# %% [markdown]
# # Filtered Datasets Specifications & Processing
# 
# ## 1. Demolition Data (DCP Housing Dataset)
# 
# ### Required Fields
# - **BIN**
# - **Job_Type**
#   - Keep only: *Demolition*, *New Building*
# - **DateFiled** and **DateComplt**
#   - Must be valid dates and fall between **01/01/2016 – 12/31/2024**
# - **Borough (Boro)**
# - **Ownership Type (`Ownership`)**
#   - Clean string values (`strip()` whitespace)
#   - Aggregate **government** and **non-profit** ownership as a proxy for *subsidized / affordable housing*
#   - Classify **private for-profit** ownership as *non-affordable housing*
# 
# ### Filtering Criteria (applied before feature engineering)
# - **Job_Status** = *5. Completed Construction*
# - **ResidFlag** = *Residential*
# - **NonresFlag** = null / missing
# - Remove records with missing **DateFiled**, **DateComplt**, or **Ownership**
# 
# ### Feature Engineering
# - **Time to Completion (`demo_duration_days`)**
#   - Calculated as: `DateComplt - DateFiled` (in days)
#   - Remove negative durations
# - **Monthly Aggregation Date (`MonthDate`)**
#   - Convert `DateComplt` to the first day of the month for easy aggregation
#   - Implemented via:
#     ```python
#     demo_eda['MonthDate'] = demo_eda['DateComplt'].values.astype('datetime64[M]')
#     ```
# - **Housing Affordability Proxy (`housing_affordability_proxy`)**
#   - Categorizes ownership into:
#     - `Affordable (Public / Non-Profit)`
#     - `Non-Affordable (Private For-Profit)`
#     - `Unknown` for uncategorized ownership
# 
# ### Final Columns to Keep
# Job_Number,
# Job_Type,
# MonthDate,
# DateFiled,
# DateComplt,
# Boro,
# ownership_clean,
# housing_affordability_proxy,
# demo_duration_days
# 
# 
# ---
# 
# ## 2. Homelessness Data (DHS Dataset)
# 
# ### Required Fields
# - **Report Date**
#   - Must be valid and fall between **01/01/2016 – 12/31/2024**
#   - Already monthly aggregated
# - **Shelter Count**
#   - Original column: `FWC Unique Individuals by Age – Total`
#   - Renamed to `shelter_count`
# 
# ### Filtering & Cleaning
# - Remove records with missing **Report Date**
# - Ensure date is parsed as `datetime` (`pd.to_datetime`)
# - Keep only relevant columns
# 
# ### Final Columns to Keep
# Report Date,
# shelter_count
# 
# 
# ---
# 
# ## 3. Standard Data Cleaning for Both Datasets
# - Ensure **date fields** are parsed as `datetime`
# - Remove **missing / NaN values** in all required fields (except `NonresFlag`)
# - Strip whitespace from string fields (e.g., `Ownership`)
# - Convert **numeric calculations** (like `demo_duration_days`) to appropriate numeric type
# 

# %%
# ------------------------------------------------------------------
# 0. Create a working copy
# ------------------------------------------------------------------
demo_eda = demo_raw.copy()

# ------------------------------------------------------------------
# 1. Ensure proper data types
# ------------------------------------------------------------------
demo_eda['DateFiled'] = pd.to_datetime(demo_eda['DateFiled'], errors='coerce')
demo_eda['DateComplt'] = pd.to_datetime(demo_eda['DateComplt'], errors='coerce')

# ------------------------------------------------------------------
# 2. Apply filtering criteria
# ------------------------------------------------------------------
demo_eda = demo_eda[
    (demo_eda['Job_Type'].isin(['New Building', 'Demolition'])) &
    (demo_eda['Job_Status'] == '5. Completed Construction') &
    (demo_eda['ResidFlag'] == 'Residential') &
    (demo_eda['NonresFlag'].isna()) &
    (demo_eda['DateFiled'].notna()) &
    (demo_eda['DateComplt'].notna()) &
    (demo_eda['DateComplt'].dt.year.between(2016, 2022))
]

# ------------------------------------------------------------------
# 3. Feature engineering: time to demolition completion & 
#    Aggregating date of completion to first of month
# ------------------------------------------------------------------
demo_eda['time_of_completion'] = (
    demo_eda['DateComplt'] - demo_eda['DateFiled']
).dt.days

# Remove invalid durations
demo_eda = demo_eda[demo_eda['time_of_completion'] >= 0]

# Creating a new column with the first day of the month
demo_eda['MonthDate'] = demo_eda['DateComplt'].values.astype('datetime64[M]')

# ------------------------------------------------------------------
# 4. Ownership cleaning
#    - Preserve all ownership categories
#    - Remove blanks / NaNs
# ------------------------------------------------------------------
demo_eda = demo_eda[demo_eda['Ownership'].notna()]

demo_eda['ownership_clean'] = demo_eda['Ownership'].str.strip()

# ------------------------------------------------------------------
# 5. Affordability proxy feature
# ------------------------------------------------------------------
public_ownership = [
    'Government, City: HPD',
    'Government, City: Partnership',
    'Government, City: City Agency',
    'Government, Unspecified: Government Agency',
    'Government, City: NYCHA/HHC',
    'Government, City: Corporation',
    'Government, City: Individual',
    'Government, City: Other',
    'Government, City: NYCHA',
    'Government, City: HHC',
    'Government, City: DCAS',
    'Government, State: NY State',
    'Government, City: SCA',
    'Government, City: Unspecified',
    'Government, City: DOE'
]

nonprofit_ownership = [
    'Private Non-Profit: Other ',
    'Private Non-Profit: Corporation',
    'Private Non-Profit: Individual',
    'Private Non-Profit: Partnership',
    'Private Non-Profit: Condo/Co-Op',
    'Private Non-Profit: Unspecified'
]

forprofit_ownership = [
    'Private For-Profit: Individual',
    'Private For-Profit: Partnership',
    'Private For-Profit: Corporation',
    'Private For-Profit: Other',
    'Private For-Profit: Condo/Co-Op',
    'Private For-Profit: Unspecified'
]

def classify_affordability(owner):
    if owner in public_ownership or owner in nonprofit_ownership:
        return 'Affordable (Government / Non-Profit)'
    elif owner in forprofit_ownership:
        return 'Non-Affordable (Private For-Profit)'
    else:
        return 'Unknown'

demo_eda['housing_affordability_proxy'] = (
    demo_eda['ownership_clean']
    .apply(classify_affordability)
)
# ------------------------------------------------------------------
# 6. Dropping BIN duplicates
# ------------------------------------------------------------------
demo_eda = demo_eda.drop_duplicates(subset='BIN')

# ------------------------------------------------------------------
# 7. Keep EDA-relevant fields
# ------------------------------------------------------------------
demo_eda = demo_eda[
    [
        'BIN',
        'Job_Type',
        'MonthDate',
        'DateFiled',
        'DateComplt',
        'Boro',
        'ownership_clean',
        'housing_affordability_proxy',
        'time_of_completion'
    ]
]

# ============================================================
# HOMELESSNESS DATA (DHS) — EDA PIPELINE
# Dataset name: homeless_raw
# ============================================================

# ------------------------------------------------------------------
# 1. Create a working copy
# ------------------------------------------------------------------
homeless_eda = homeless_raw.copy()

# ------------------------------------------------------------------
# 2. Ensure proper data types
# ------------------------------------------------------------------
homeless_eda['Report Date'] = pd.to_datetime(
    homeless_eda['Report Date'],
    errors='coerce'
)

# ------------------------------------------------------------------
# 3. Filter to study period (already monthly aggregated)
# ------------------------------------------------------------------
homeless_eda = homeless_eda[
    (homeless_eda['Report Date'].notna()) &
    (homeless_eda['Report Date'].dt.year.between(2016, 2022))
]

# ------------------------------------------------------------------
# 4. Keep and rename core field
# ------------------------------------------------------------------
homeless_eda = homeless_eda[
    ['Report Date', 'FWC Unique Individuals by Age - Total']
].rename(
    columns={'FWC Unique Individuals by Age - Total': 'shelter_count'}
)

# ------------------------------------------------------------------
# 5. Keeping EDA-relevant fields
# ------------------------------------------------------------------

homeless_eda = homeless_eda[
    [
    'Report Date',
    'shelter_count'
    ]
]

# ============================================================
# FINAL EDA DATASETS
# ============================================================

# demo_eda         → building-level demolition data
# homeless_eda     → monthly shelter population (already aggregated)




# %%
# removing periods and commas from shelter_count and convering to integer
homeless_eda['shelter_count'] = homeless_eda['shelter_count'].str.replace('.','').str.replace(',','').astype(int)

# %%
# checking BIN count
demo_eda['BIN'].count()
# %% [markdown]
# # CREATING FACT / DIM TABLE FOR STAR SCHEMA

# %%
# OWNERSHIP COLUMN INTO DIMENSION TABLE
    # finding all unique values of ownership column, removing all characters outside of 'Government', 'Private Non-Profit', 'Private For-Profit'
unique_ownership = demo_eda['ownership_clean'].apply(lambda x: x.split(':')[0])
unique_ownership = unique_ownership.apply(lambda x: x.split(',')[0]).unique()
unique_ownership = pd.DataFrame({'Ownership_ID': [1,2,3], 'ownership_clean':unique_ownership})
    # creates a dataframe to merge with that has ownership ID and each unique type of ownership
unique_ownership

# JOB_TYPE COLUMN INTO DIMENSION TABLE
unique_jobtype = pd.DataFrame({'Job_TypeID': [1,2], 'Job_Type':demo_eda['Job_Type'].unique()})
    # dataframe to merge with Job_TypeID with each unique type of Job_Type
unique_jobtype

# MERGE BACK TO FACT TABLE
fact_demolitions = demo_eda[['BIN','Job_Type','ownership_clean','Boro','MonthDate','DateFiled','DateComplt','time_of_completion']]
fact_demolitions['ownership_clean'] = fact_demolitions['ownership_clean'].apply(lambda x: x.split(':')[0])
fact_demolitions['ownership_clean'] = fact_demolitions['ownership_clean'].apply(lambda x: x.split(',')[0])
fact_demolitions = fact_demolitions.merge(unique_ownership[['Ownership_ID','ownership_clean']],on='ownership_clean',how='left')
fact_demolitions = fact_demolitions.merge(unique_jobtype[['Job_TypeID','Job_Type']], on='Job_Type',how='left')
fact_demolitions = fact_demolitions.drop(columns={'ownership_clean','Job_Type'},axis=1)

# MAPPING 'Boro' COLUMN TO ITS BOROUGH CODE ON DATA DICTIONARY
boromap = {1:'Manhattan',2:'Bronx',3:'Brooklyn',4:'Queens',5:'Staten Island'}
fact_demolitions['Boro'] = fact_demolitions['Boro'].map(boromap)

fact_demolitions = fact_demolitions[['MonthDate','BIN','Job_TypeID','Ownership_ID','Boro','DateFiled','DateComplt','time_of_completion']]


# changing format of times to not include days
#fact_demolitions['MonthDate'] = fact_demolitions['MonthDate'].dt.strftime('%m/%Y')
#homeless_eda['Report Date'] = homeless_eda['Report Date'].dt.strftime('%m/%Y')


# renaming columns to remove spaces / add underlines / make more interpretable
fact_demolitions.rename(columns={'MonthDate':'Month_Date','Boro':'Borough','DateFiled':'Date_Filed','DateComplt':'Date_Completed'},inplace=True)
homeless_eda.rename(columns={'Report Date':'Report_Date'},inplace=True)

# quick clean to make all headers lowercase
fact_demolitions.columns = map(str.lower, fact_demolitions.columns)
homeless_eda.columns = map(str.lower, homeless_eda.columns)
unique_jobtype.columns = map(str.lower, unique_jobtype.columns)
unique_ownership.columns = map(str.lower, unique_ownership.columns)

# fixing datatypes to avoid errors when inserting into SQL table
fact_demolitions['borough'] = fact_demolitions['borough'].astype('string')


# all of the tables for the SQL, two dim, two fact
#display(fact_demolitions.head(),unique_ownership.head(),unique_jobtype.head(), homeless_eda.head())

# PATHS TO PROCESSED DIMENSION/FACT TABLES
processed_jobtypedim = "/Users/beans/Desktop/TeamHousing/data/processed/dim_jobtype.csv"
processed_ownershipdim = "/Users/beans/Desktop/TeamHousing/data/processed/dim_ownership.csv"
processed_fact_demolitions = "/Users/beans/Desktop/TeamHousing/data/processed/fact_demolitions.csv"
processed_homeless_eda = "/Users/beans/Desktop/TeamHousing/data/processed/fact_shelter.csv"


unique_jobtype.to_csv(processed_jobtypedim,index=False)
unique_ownership.to_csv(processed_ownershipdim,index=False)
fact_demolitions.to_csv(processed_fact_demolitions,index=False)
homeless_eda.to_csv(processed_homeless_eda,index=False)

# %%
# CONNECTING TO DATABASE AND IMPORTING DATA
import sqlite3


# PATH TO DATABASE
databasepath = "/Users/beans/Desktop/TeamHousing/data/processed/nyc_demolitions.db"
conn = sqlite3.connect(databasepath)

# LOADING CSV DATA
# using if_exists append to remain with same schema
unique_jobtype.to_sql('dim_jobtype', conn, if_exists='append',index=False)
unique_ownership.to_sql('dim_ownership', conn, if_exists='append',index=False)
fact_demolitions.to_sql('fact_demolitions', conn, if_exists='append',index=False)
homeless_eda.to_sql('fact_shelters', conn, if_exists='append',index=False)

conn.close()




