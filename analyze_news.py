import base64
from io import BytesIO

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util

# Load dataset
df = pd.read_csv('energy_news.csv')

# Combine title and summary for model analysis
def combine_text(row):
    title = str(row.get("title", ""))
    summary = str(row.get("summary", ""))
    return f"{title} {summary}".strip()

texts = df.apply(combine_text, axis=1).tolist()

# Use a transformer model to embed the articles and category anchors
model = SentenceTransformer("all-MiniLM-L6-v2")

# Article embeddings
embeddings = model.encode(texts, convert_to_tensor=True)

# Anchor texts describing each category
anchors = {
    "Political": "government policy regulation law congress president diplomacy",
    "Economic": "economy market business investment finance industry trade gdp",
    "Energy": "energy renewable clean gas oil solar wind power grid battery",
    "China": "china chinese beijing shanghai xi huawei sino technology economy",
}

# Encode anchor texts
anchor_embeds = {c: model.encode(t, convert_to_tensor=True) for c, t in anchors.items()}

# Calculate mean cosine similarity between articles and each anchor
scores = {}
for cat, anchor_emb in anchor_embeds.items():
    sim = util.cos_sim(embeddings, anchor_emb)
    scores[cat] = float(sim.mean())

# Normalize scores
values = np.array(list(scores.values()), dtype=float)
min_val = values.min()
values = values - min_val
values_normalized = values / values.sum() if values.sum() != 0 else values

# Radar chart setup
labels = list(scores.keys())
num_labels = len(labels)
angles = np.linspace(0, 2 * np.pi, num_labels, endpoint=False).tolist()
values_plot = values_normalized.tolist()
values_plot += values_plot[:1]
angles += angles[:1]

fig, ax = plt.subplots(subplot_kw=dict(polar=True))
ax.plot(angles, values_plot, 'o-', linewidth=2)
ax.fill(angles, values_plot, alpha=0.25)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, values_normalized.max() * 1.1)
ax.set_title('Energy News Analysis')
plt.tight_layout()

# Save chart to a base64 text file to avoid binary files in the repository
buf = BytesIO()
plt.savefig(buf, format='png')
b64_data = base64.b64encode(buf.getvalue()).decode('utf-8')
with open('radar_chart_base64.txt', 'w') as f:
    f.write(b64_data)
print('Radar chart encoded to radar_chart_base64.txt')
