"""Analyze energy news articles using a language model.

For each article, the script queries an LLM to assess four dimensions:
political intensity, economic drive, energy relevance and China correlation.
Scores are stored alongside the original data and a radar chart for each
article is saved as base64-encoded text.
"""

import os
import json
import base64
from io import BytesIO

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is required")

# Load dataset
DF_PATH = "energy_news.csv"
df = pd.read_csv(DF_PATH)


def combine_text(row):
    title = str(row.get("title", ""))
    summary = str(row.get("summary", ""))
    return f"{title} {summary}".strip()


def query_llm(text: str) -> dict:
    """Query the language model to score the article on four dimensions."""
    prompt = (
        "Please score the following news article on a scale from 0 to 1 inclusive "
        "for these four dimensions: Political intensity, Economic drive, Energy "
        "relevance, and China correlation. Respond strictly with JSON in the form\n"
        "{\"political\":0,\"economic\":0,\"energy\":0,\"china\":0}.\n\n"
        f"Article: {text}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response["choices"][0]["message"]["content"]
    data = json.loads(content)
    return {
        "political": float(data.get("political", 0)),
        "economic": float(data.get("economic", 0)),
        "energy": float(data.get("energy", 0)),
        "china": float(data.get("china", 0)),
    }


# Prepare output directory
os.makedirs("llm_radar_charts", exist_ok=True)

# Process each article
scores = []
for idx, row in df.iterrows():
    text = combine_text(row)
    result = query_llm(text)
    for key, val in result.items():
        df.loc[idx, key] = val
    # Create radar chart
    labels = ["Political", "Economic", "Energy", "China"]
    values = [result["political"], result["economic"], result["energy"], result["china"]]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_plot = values + values[:1]
    angles_plot = angles + angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles_plot, values_plot, "o-", linewidth=2)
    ax.fill(angles_plot, values_plot, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles), labels)
    ax.set_ylim(0, 1)
    ax.set_title(f"Article {idx}")
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    with open(f"llm_radar_charts/article_{idx}.txt", "w") as f:
        f.write(b64)
    plt.close(fig)

# Save dataframe with scores
output_csv = "energy_news_scored.csv"
df.to_csv(output_csv, index=False)
print(f"Saved scores to {output_csv} and charts to llm_radar_charts/")
