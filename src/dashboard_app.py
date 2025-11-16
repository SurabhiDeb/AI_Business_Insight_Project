import streamlit as st
import pandas as pd
import os
import textwrap  # Used for formatting AI text output


# Set the page configuration for a better look
st.set_page_config(layout="wide", page_title="AI Business Insights Dashboard")

# --- FILE PATH SETUP ---
# Ensure relative paths work correctly when running from the 'src' directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)


@st.cache_data
def load_all_data():
    """Loads data from the three necessary output files."""

    # --- 1. Load Overall KPIs ---
    overall_kpis_path = os.path.join(PROJECT_ROOT, "data", "overall_kpis.csv")
    overall_kpis_df = pd.read_csv(overall_kpis_path)

    # Convert the single-row DataFrame into an easy-to-access dictionary
    overall = overall_kpis_df.to_dict(orient='records')[0]

    # --- 2. Load Regional Summary (for the table and charts) ---
    summary_path = os.path.join(PROJECT_ROOT, "data", "summary.csv")
    summary_df = pd.read_csv(summary_path)

    # --- 3. Load AI Insight Text ---
    insights_path = os.path.join(PROJECT_ROOT, "data", "insights.txt")
    try:
        with open(insights_path, 'r', encoding='utf-8') as f:
            ai_text = f.read()
            # Wrap text for better display if it's very long
            ai_text = textwrap.fill(ai_text, 120)
    except FileNotFoundError:
        ai_text = "AI insight file not found. Please run src/ai_insight_generator.py first."

    return overall, summary_df, ai_text


try:
    # Load all required data
    overall_kpis, region_summary_df, ai_summary_text = load_all_data()
except Exception as e:
    st.error(
        f"Error loading data files. Please ensure you have run both database_setup.py and etl_pipeline.py. Details: {e}")
    st.stop()


# --- DASHBOARD LAYOUT ---
st.title(" AI-Powered Business Insight Dashboard")
st.markdown("---")


# 1. AI-Generated Summary (Displayed prominently first)
st.subheader(" AI-Generated Executive Summary")
st.success(ai_summary_text)
st.markdown("---")


# 2. KPI Cards (Using data from overall_kpis and region_summary)
st.subheader(f"Latest Month KPIs ({overall_kpis['latest_month']})")

# Calculate the overall profit margin for the KPI card
profit_margin = (overall_kpis['total_profit'] /
                 overall_kpis['total_revenue']) * 100

# Determine the Top Region by Target Achievement
# idxmax() finds the index of the row with the maximum value
top_region_row = region_summary_df.loc[region_summary_df['target_achievement_pct'].idxmax(
)]
top_region = f"{top_region_row['region']} ({top_region_row['target_achievement_pct']:.0f}%)"

# Determine the Lowest Profit Margin Region
# idxmin() finds the index of the row with the minimum value
lowest_margin_region = region_summary_df.loc[region_summary_df['profit_margin'].idxmin(
)]['region']


# Display KPIs using columns
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"€{overall_kpis['total_revenue']:.0f}"  # Display as integer for clarity
)

col2.metric(
    "Overall Profit Margin",
    f"{profit_margin:.2f}%"
)

col3.metric(
    "Top Target Achiever",
    top_region
)

col4.metric(
    "Lowest Profit Region",
    lowest_margin_region
)


# 3. Regional Data Table
st.markdown("---")
st.subheader(" Detailed Regional Performance Data")
st.info("Performance is for the latest month and merged with targets.")

# Format the dataframe for display
display_df = region_summary_df.rename(columns={
    'revenue': 'Revenue (€)',
    'profit': 'Profit (€)',
    'quantity': 'Quantity Sold',
    'revenue_target': 'Target (€)',
    'profit_margin': 'Profit Margin (%)',
    'target_achievement_pct': 'Target Achievement (%)'
})

# Select and reorder columns for optimal table display
display_df = display_df[[
    'region', 'Revenue (€)', 'Profit (€)', 'Profit Margin (%)', 'Target (€)',
    'Target Achievement (%)', 'Quantity Sold'
]]

# Apply formatting for currency and percentages
st.dataframe(
    display_df,
    column_config={
        "Revenue (€)": st.column_config.NumberColumn(format="€%.0f"),
        "Profit (€)": st.column_config.NumberColumn(format="€%.0f"),
        "Target (€)": st.column_config.NumberColumn(format="€%.0f"),
        "Profit Margin (%)": st.column_config.NumberColumn(format="%.2f%%"),
        "Target Achievement (%)": st.column_config.NumberColumn(format="%.0f%%"),
        "region": st.column_config.TextColumn("Region"),
    },
    hide_index=True
)


# 4. Charts
st.markdown("---")
st.subheader("Visualization: Target Achievement vs. Profit Margin")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.caption("Target Achievement by Region")
    st.bar_chart(
        region_summary_df,
        x="region",
        y="target_achievement_pct",
        color="#32a852"  # Green for achievement
    )

with chart_col2:
    st.caption("Regional Profit Margin")
    st.bar_chart(
        region_summary_df,
        x="region",
        y="profit_margin",
        color="#3498db"  # Blue for profit
    )

st.markdown("---")
st.caption(
    f"Data Source: SQLite Database via ETL. Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
