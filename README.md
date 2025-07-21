# Politics AI

This repository provides a simple script to collect global energy news using [NewsAPI](https://newsapi.org/). It fetches articles within a date range, extracts the title, summary, publisher, date and URL, and saves the results to `energy_news.csv`.

## Requirements

- Python 3.8+
- `requests`
- `pandas`
- `sentence-transformers`
- A NewsAPI API key

## Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export your NewsAPI key as an environment variable:

```bash
export NEWSAPI_KEY="036a4eee25964a9bb2a2804c6ddf0685"
```

3. Run the script:

```bash
python main.py
```

The script will fetch news from July 5 to July 8, 2025 related to global energy, clean energy, traditional energy and energy policy. Results are stored in `energy_news.csv`.

## Analyzing the News

After running `main.py`, analyze the articles and generate a radar chart showing political intensity, economic drive, energy relevance and China correlation:

```bash
python analyze_news.py
```

The script uses a transformer model to gauge political, economic, energy and
China-related relevance. A radar chart is created and encoded to base64 text in
`radar_chart_base64.txt`.

To view the chart as an image:

```bash
base64 -d radar_chart_base64.txt > radar_chart.png
```

Alternatively, you can analyze each article individually using a language model.
Export your OpenAI API key and run `analyze_news_llm.py`:

```bash
export OPENAI_API_KEY="sk-..."
python analyze_news_llm.py
```

This script queries an LLM for every article, saves scores in
`energy_news_scored.csv`, and creates one radar chart per article encoded as
base64 text files in the `llm_radar_charts` directory.
