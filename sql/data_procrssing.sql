-- Dimension table for each ownership within demolition data
CREATE TABLE dim_ownership (
  ownership_id INTEGER PRIMARY KEY, -- Surrogate Key
  ownership_clean TEXT UNIQUE -- contains each unique construction/demolition ownership
);


-- Dimension  table for the job types within demolition data
CREATE TABLE dim_jobtype (
  job_typeid TEXT PRIMARY KEY,
  job_type TEXT UNIQUE
);

-- Central fact table for demolitions
CREATE TABLE fact_demolitions (
  month_date DATE, --contains the month and year of event
  job_number TEXT PRIMARY KEY,
  job_typeid INTEGER,
  ownership_id INTEGER,
  borough TEXT,
  date_filed DATE,
  date_completed DATE,
  time_of_completion INTEGER,

  FOREIGN KEY (job_typeid) REFERENCES dim_jobtype(job_typeid),
  FOREIGN KEY (ownership_id) REFERENCES dim_ownership(ownership_id)
);

CREATE TABLE fact_shelters (
  report_date DATETIME,
  shelter_count INT
)


