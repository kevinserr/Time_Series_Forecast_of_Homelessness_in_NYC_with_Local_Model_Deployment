import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# ---------------------------------------------------
# 1️⃣ PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Time Series Model Comparison", layout="wide")
st.title("Time Series Forecast Comparison (2016–2022, 80/20 Split)")

# ---------------------------------------------------
# 2️⃣ LOAD + FILTER DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("../../data/processed/fact_shelter.csv")
    exog = pd.read_csv("../data/datedf.csv")

    # Convert to datetime
    data["report_date"] = pd.to_datetime(data["report_date"])
    exog["month_date"] = pd.to_datetime(exog["month_date"])

    # Set index
    data = data.set_index("report_date").sort_index()
    exog = exog.set_index("month_date").sort_index()

    # Filter 2016–2022
    data = data.loc["2016-01-01":"2022-12-31"]
    exog = exog.loc["2016-01-01":"2022-12-31"]

    return data, exog

data, exog = load_data()

# Select your target column explicitly
target = data  # <- Replace with actual column name

# Keep exogenous as DataFrame
exog = exog[['covid_dummy']]

# ---------------------------------------------------
# 3️⃣ 80 / 20 TRAIN TEST SPLIT
# ---------------------------------------------------
train_size = int(len(target) * 0.8)
train = target.iloc[:train_size]
test = target.iloc[train_size:]

train_exog = exog.iloc[:train_size]
test_exog = exog.iloc[train_size:]

# ---------------------------------------------------
# 4️⃣ LOAD PICKLED FITTED MODELS
# ---------------------------------------------------
@st.cache_resource
def load_models():
    arima = joblib.load(open("../pickles/arima_model.pkl", "rb"))
    sarima = joblib.load(open("../pickles/sarima_model.pkl", "rb"))
    sarimax = joblib.load(open("../pickles/sarimax_model.pkl", "rb"))
    return arima, sarima, sarimax

arima_model, sarima_model, sarimax_model = load_models()

# ---------------------------------------------------
# 5️⃣ FORECAST FUNCTION
# ---------------------------------------------------
def forecast_model(model_name):
    if model_name == "ARIMA":
        forecast = arima_model.get_forecast(steps=len(test)).predicted_mean
    elif model_name == "SARIMA":
        forecast = sarima_model.get_forecast(steps=len(test)).predicted_mean
    elif model_name == "SARIMAX":
        forecast = sarimax_model.get_forecast(steps=len(test), exog=test_exog).predicted_mean
    else:
        raise ValueError("Unknown model name")
    return forecast

# ---------------------------------------------------
# 6️⃣ PLOT FUNCTION
# ---------------------------------------------------
from sklearn.metrics import mean_squared_error
import numpy as np

def plot_results(model_name):
    forecast = forecast_model(model_name)

    # Ensure all series are pandas Series with proper names
    train_series = train.squeeze().rename("Train")
    test_series = test.squeeze().rename("Test")
    forecast_series = forecast.squeeze().rename(f"{model_name} Forecast")

    # Compute RMSE using sklearn
    rmse = np.sqrt(mean_squared_error(test_series.values, forecast_series.values))
    rmse = round(rmse,2)
    # Combine into a clean DataFrame for st.line_chart
    combined_data = pd.concat([train_series, test_series, forecast_series], axis=1)
    combined_data = combined_data.reindex(train.index.union(test.index))  # align index

    # Streamlit line_chart
    st.subheader(f"{model_name} Forecast vs Actual (st.line_chart)")
    st.line_chart(combined_data)

    # Matplotlib plot
    st.subheader(f"{model_name} Forecast vs Actual (matplotlib)")
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(train_series.index, train_series.values, label="Train", color="blue")
    ax.plot(test_series.index, test_series.values, label="Test", color="black")
    ax.plot(forecast_series.index, forecast_series.values, label=f"{model_name} Forecast", color="red")
    ax.set_title(f"{model_name} Forecast vs Actual")
    ax.legend()
    st.pyplot(fig)

    # Display RMSE below
    st.write(f"**RMSE for {model_name}:** {rmse} people in shelter counts.")

# ---------------------------------------------------
# 7️⃣ BUTTONS
# ---------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("ARIMA"):
        plot_results("ARIMA")

with col2:
    if st.button("SARIMA"):
        plot_results("SARIMA")

with col3:
    if st.button("SARIMAX"):
        plot_results("SARIMAX")