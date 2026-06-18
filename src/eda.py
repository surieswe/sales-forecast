import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import seasonal_decompose

# Load data
df = pd.read_csv("data/sales_data.csv")

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Set date as index
df = df.set_index("date")

# -------------------------------
# 1. Basic Statistics
# -------------------------------
print("\nBasic Statistics:")
print(df.describe())

# -------------------------------
# 2. Time Series Plot
# -------------------------------
fig = px.line(
    df,
    x=df.index,
    y="sales",
    title="Sales Over Time"
)
fig.show()

# -------------------------------
# 3. Time Series Decomposition
# -------------------------------
decomposition = seasonal_decompose(
    df["sales"],
    model="additive",
    period=365
)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df.index,
    y=decomposition.trend,
    name="Trend"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=decomposition.seasonal,
    name="Seasonality"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=decomposition.resid,
    name="Residual"
))

fig.update_layout(title="Time Series Decomposition")
fig.show()

# -------------------------------
# 4. Monthly Sales
# -------------------------------
monthly = df.resample("M").sum()

fig = px.bar(
    monthly,
    x=monthly.index,
    y="sales",
    title="Monthly Sales"
)

fig.show()