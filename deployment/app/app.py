import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error
import plotly.graph_objects as go

# ---------------------------------------------------
# 1️⃣ PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="SARIMAX Forecast App", layout="wide")
st.title("SARIMAX Forecast with Multiple Exogenous Models")

# ---------------------------------------------------
# 2️⃣ LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("../../data/processed/fact_shelter.csv")
    exog = pd.read_csv("../data/datedf.csv")

    data["report_date"] = pd.to_datetime(data["report_date"])
    exog["month_date"] = pd.to_datetime(exog["month_date"])

    data = data.set_index("report_date").sort_index()
    exog = exog.set_index("month_date").sort_index()

    data = data.loc["2016-01-01":"2022-12-31"]
    exog = exog.loc["2016-01-01":"2022-12-31"]

    return data, exog

data, exog = load_data()
target = data.squeeze()

# ---------------------------------------------------
# 3️⃣ SIDEBAR TOGGLES (RESTORED ORIGINAL VERSION)
# ---------------------------------------------------
st.sidebar.header("Exogenous Variables")
st.sidebar.info(
    "Select which exogenous variables to include in the forecast.\n"
    "The app will automatically choose the correct SARIMAX model."
)

use_covid = st.sidebar.checkbox("Include covid_dummy", value=True)
use_affordable = st.sidebar.checkbox("Include affordable_demo", value=True)

exog_cols = ['covid_dummy', 'affordable_demo']

with st.sidebar.expander("What are these exogenous variables?"):
    st.markdown("""
**covid_dummy**  
Binary variable indicating months affected by COVID-19 disruptions.  
Used to capture structural breaks and abnormal demand shifts.

**affordable_demo**  
Indicator related to affordable housing demolitions.  

These variables allow the SARIMAX model to adjust forecasts based on 
external shocks and policy influences.
""")

# ---------------------------------------------------
# 4️⃣ TRAIN / TEST SPLIT
# ---------------------------------------------------
train_size = int(len(target) * 0.8)
train = target.iloc[:train_size]
test = target.iloc[train_size:]

train_exog = exog[exog_cols].iloc[:train_size].copy()
test_exog = exog[exog_cols].iloc[train_size:].copy()

# ---------------------------------------------------
# 5️⃣ LOAD THE CORRECT SARIMAX MODEL
# ---------------------------------------------------
def load_model_by_exog(covid: bool, affordable: bool):
    if covid and affordable:
        filename = "../data/sarimax_both.pkl"
    elif covid and not affordable:
        filename = "../data/sarimax_covid.pkl"
    elif not covid and affordable:
        filename = "../data/sarimax_aff.pkl"
    else:
        filename = "../data/sarimax_none.pkl"
    return joblib.load(open(filename, "rb"))

@st.cache_resource
def get_model(covid, affordable):
    return load_model_by_exog(covid, affordable)

sarimax_model = get_model(use_covid, use_affordable)

# ---------------------------------------------------
# 6️⃣ PREPARE EXOG FOR FORECAST
# ---------------------------------------------------
expected_cols = sarimax_model.model.exog_names if sarimax_model.model.k_exog > 0 else []
forecast_exog = test_exog[expected_cols].iloc[:len(test)] if expected_cols else None

# ---------------------------------------------------
# 7️⃣ FORECAST
# ---------------------------------------------------
forecast_obj = sarimax_model.get_forecast(steps=len(test), exog=forecast_exog)
forecast = forecast_obj.predicted_mean
conf_int = forecast_obj.conf_int()

# ---------------------------------------------------
# 8️⃣ METRICS
# ---------------------------------------------------
rmse = np.sqrt(mean_squared_error(test.values, forecast.values))
rmse = round(rmse, 2)

# ---------------------------------------------------
# 9️⃣ INTERACTIVE PLOT WITH PLOTLY
# ---------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=train.index, y=train.values, mode='lines', name='Train'))
fig.add_trace(go.Scatter(x=test.index, y=test.values, mode='lines', name='Test'))
fig.add_trace(go.Scatter(x=forecast.index, y=forecast.values, mode='lines', name='Forecast'))

fig.update_layout(
    title="SARIMAX Forecast (1,0,0) (1,1,0,12)",
    xaxis_title="Date",
    yaxis_title="Shelter Count"
)

# ---------------------------------------------------
# 🔟 DISPLAY METRICS + PLOT
# ---------------------------------------------------
col1, col2 = st.columns([1,2])
col1.metric("RMSE", round(rmse), "Average Error in Predicted Shelter Count")
col2.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# 1️⃣1️⃣ MODEL SUMMARY
# ---------------------------------------------------
with st.expander("View SARIMAX Model Summary"):
    st.text(sarimax_model.summary())

# ---------------------------------------------------
# DOWNLOAD FORECAST + KPI CARDS
# ---------------------------------------------------
forecast_df = pd.DataFrame({
    "forecast": forecast.values,
}, index=forecast.index)

col1, col2, col3 = st.columns(3)
col1.metric("Train Size", len(train))
col3.metric("Test Size", len(test))