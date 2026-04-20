import requests
from rapidfuzz import fuzz
from config import NEWS_API_KEY

def fetch_headlines(topic: str, num: int = 20) -> list[dict]:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": num,
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return data.get("articles", [])


def deduplication(articles: list[dict], threshold: int = 85) -> list[dict]:
    seen_headlines = []
    unique_articles = []

    for article in articles:
        headline = article.get("title", "")
        if not headline or headline == "[Removed]":
            continue

        is_duplicate = False
        for seen in seen_headlines:
            similarity = fuzz.ratio(headline.lower(), seen.lower())
            if similarity >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            seen_headlines.append(headline)
            unique_articles.append(article)

    return unique_articles