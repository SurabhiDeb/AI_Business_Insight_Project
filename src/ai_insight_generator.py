# src/ai_insight_generator.py
import pandas as pd
from transformers import pipeline
import textwrap


def read_kpi():
    summary = pd.read_csv('../data/summary.csv')
    overall = pd.read_csv(
        '../data/overall_kpis.csv').to_dict(orient='records')[0]
    return summary, overall


def build_prompt(summary_df, overall):
    table_text = summary_df.to_string(index=False)
    prompt = f"""
You are a professional business analyst. Here are KPI metrics for the latest month ({overall['latest_month']}):
Overall total revenue: {overall['total_revenue']:.2f}
Overall total profit: {overall['total_profit']:.2f}

Regional breakdown:
{table_text}

Write a concise 5-sentence executive summary (professional tone) that:
- highlights the best and worst performing region(s),
- comments on profit margin and target achievement,
- suggests one or two actionable recommendations.
Keep it suitable to present to a Sales Director.
"""
    return prompt


def generate_insight(prompt, model_name="distilgpt2", max_length=180):
    generator = pipeline("text-generation", model=model_name)
    out = generator(prompt, max_length=max_length, num_return_sequences=1)
    text = out[0]['generated_text']
    # cleanup: remove leading prompt if produced (some models repeat)
    generated = text[len(prompt):].strip(
    ) if text.startswith(prompt) else text.strip()
    return textwrap.fill(generated, 100)


if __name__ == "__main__":
    summary, overall = read_kpi()
    prompt = build_prompt(summary, overall)
    insight = generate_insight(prompt)
    with open('../data/insights.txt', 'w', encoding='utf-8') as f:
        f.write(insight)
    print("Generated AI insight and saved to ../data/insights.txt")
    print(insight)
