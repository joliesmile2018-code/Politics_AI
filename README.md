# Politics AI

This repository provides a simple script to collect global energy news using [NewsAPI](https://newsapi.org/). It fetches articles within a date range, extracts the title, summary, publisher, date and URL, and saves the results to `energy_news.csv`.

## Requirements

- Python 3.8+
- `requests`
- `pandas`
- A NewsAPI API key

## Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export your NewsAPI key as an environment variable:

```bash
export NEWSAPI_KEY=your_key_here
```

3. Run the script:

```bash
python main.py
```

The script will fetch news from July 5 to July 8, 2025 related to global energy, clean energy, traditional energy and energy policy. Results are stored in `energy_news.csv`.
