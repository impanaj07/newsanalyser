from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(articles: list[dict]) -> list[dict]:
    results = []

    for article in articles:
        headline = article.get("title", "")
        if not headline or headline == "[Removed]":
            continue

        scores = analyzer.polarity_scores(headline)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "Positive 😊"
        elif compound <= -0.05:
            label = "Negative 😟"
        else:
            label = "Neutral 😐"

        results.append({
            "headline": headline,
            "source": article.get("source", {}).get("name", "Unknown"),
            "compound": compound,
            "label": label,
            "url": article.get("url", ""),
        })

    return results