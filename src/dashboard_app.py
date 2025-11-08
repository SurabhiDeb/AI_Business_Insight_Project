import streamlit as st
import pandas as pd
import os

# --- Load CSV ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "../data/summary.csv")

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    st.error(f"CSV file not found at {csv_path}")
    st.stop()

st.title("Business Dashboard")

# --- KPI Cards ---
st.subheader("Key Performance Indicators")

# Extract KPI values
revenue = df.loc[df['Metric'] == 'Total Revenue', 'Value'].values[0]
profit = df.loc[df['Metric'] == 'Profit Margin', 'Value'].values[0]
top_region = df.loc[df['Metric'] == 'Top Region', 'Value'].values[0]
under_product = df.loc[df['Metric'] ==
                       'Underperforming Product', 'Value'].values[0]

# Display KPIs using columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue (€)", revenue)
col2.metric("Profit Margin (%)", profit)
col3.metric("Top Region", top_region)
col4.metric("Underperforming Product", under_product)

# --- Table View ---
st.subheader("Key Performance Data Table")
st.dataframe(df)

# --- Simple Chart ---
st.subheader("Revenue by Region (Sample Data)")
chart_data = pd.DataFrame({
    "Region": ["North", "South", "East", "West"],
    "Revenue": [150000, 120000, 90000, 80000]
})
st.bar_chart(chart_data.set_index("Region"))

# --- AI-generated summary ---
st.subheader("AI-Generated Text Summary")
summary_text = (
    f"This month, total revenue is €{revenue}, "
    f"with a profit margin of {profit}%. "
    f"The top-performing region is {top_region}, "
    f"while {under_product} is underperforming. "
    f"Focus on high-performing areas to improve next month."
)
st.write(summary_text)
