import os
import requests
import pandas as pd

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")


def search_news(query: str, start_date: str, end_date: str, language: str = "en", sources=None):
    """Fetch news articles from NewsAPI."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": start_date,
        "to": end_date,
        "language": language,
        "sortBy": "relevancy",
        "apiKey": NEWSAPI_KEY,
        "pageSize": 100,
    }
    if sources:
        params["sources"] = ",".join(sources)

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("articles", [])


def build_dataframe(articles):
    rows = []
    for art in articles:
        rows.append({
            "title": art.get("title"),
            "summary": art.get("description"),
            "source": art.get("source", {}).get("name"),
            "published_at": art.get("publishedAt"),
            "url": art.get("url"),
        })
    return pd.DataFrame(rows)


def main():
    if not NEWSAPI_KEY:
        raise EnvironmentError("NEWSAPI_KEY environment variable is required")

    query = (
        "global energy OR \"clean energy\" OR \"renewable energy\" "
        "OR \"energy policy\" OR \"traditional energy\""
    )
    start_date = "2025-07-05"
    end_date = "2025-07-08"

    articles = search_news(query, start_date, end_date)
    df = build_dataframe(articles)
    df.to_csv("energy_news.csv", index=False)
    print(df)


if __name__ == "__main__":
    main()
