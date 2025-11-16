import pandas as pd
import os
import textwrap
from transformers import pipeline

# --- FILE PATH SETUP ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SUMMARY_PATH = os.path.join(DATA_DIR, 'summary.csv')
OVERALL_KPI_PATH = os.path.join(DATA_DIR, 'overall_kpis.csv')
INSIGHTS_PATH = os.path.join(DATA_DIR, 'insights.txt')

# --- 1. Load Data ---
try:
    summary_df = pd.read_csv(SUMMARY_PATH)
    overall_kpis = pd.read_csv(OVERALL_KPI_PATH).to_dict(orient='records')[0]
except FileNotFoundError as e:
    print(
        f"FATAL ERROR: Could not find required data files. Run etl_pipeline.py first. Details: {e}")
    exit()

# --- 2. Determine Key Findings ---

# Overall Metrics
total_revenue = overall_kpis['total_revenue']
profit_margin = (overall_kpis['total_profit'] /
                 overall_kpis['total_revenue']) * 100
latest_month = overall_kpis['latest_month']

# Regional Metrics
top_achiever = summary_df.loc[summary_df['target_achievement_pct'].idxmax()]
lowest_margin = summary_df.loc[summary_df['profit_margin'].idxmin()]

# --- 3. Construct Prompt for LLM ---
prompt = textwrap.dedent(f"""
    Generate a concise, professional executive summary for the latest business performance in {latest_month}.
    
    Overall Performance:
    - Total Revenue: €{total_revenue:,.0f}
    - Overall Profit Margin: {profit_margin:.2f}%
    
    Key Regional Insights:
    - Top Target Achiever: {top_achiever['region']} achieved {top_achiever['target_achievement_pct']:.0f}% of target.
    - Lowest Profit Margin: {lowest_margin['region']} had the lowest margin at {lowest_margin['profit_margin']:.2f}%.
    
    Based on this data, provide an executive summary focusing on the best performing region and the region requiring immediate attention.
    Start directly with the summary, do not include a title or introduction. Keep it under 100 words.
    """)

# --- 4. Generate Text using LLM (distilgpt2) ---
try:
    # Initialize the text generation pipeline
    generator = pipeline("text-generation", model="distilgpt2")

    # Generate text
    result = generator(
        prompt.strip(),
        max_length=150,  # Set max length appropriate for "under 100 words"
        num_return_sequences=1,
        truncation=True
    )

    # Extract and clean the generated text
    generated_text = result[0]['generated_text'].replace(
        prompt.strip(), '').strip()

    # Simple cleanup to prevent model repetition and ensure a clean paragraph
    if generated_text.startswith('-'):
        generated_text = generated_text.split('\n')[0]

except Exception as e:
    # Fallback if the transformers model fails (e.g., dependency error)
    generated_text = f"Automated insight generation failed ({e}). However, the data shows excellent performance in {top_achiever['region']} (Target Achievement: {top_achiever['target_achievement_pct']:.0f}%), while {lowest_margin['region']} requires immediate review due to a low profit margin of {lowest_margin['profit_margin']:.2f}%."


# --- 5. Save the Insight ---
try:
    # Wrap text for display formatting
    final_insight = textwrap.fill(generated_text, 120)

    with open(INSIGHTS_PATH, 'w', encoding='utf-8') as f:
        f.write(final_insight)

    print(f"Generated AI insight and saved to {INSIGHTS_PATH}")
except Exception as e:
    print(f"FATAL ERROR: Could not write insight to file. Details: {e}")
