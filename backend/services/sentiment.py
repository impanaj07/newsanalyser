from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()#initializes an instance of the SentimentIntensityAnalyzer class from the vaderSentiment library, which is used to perform sentiment analysis on text data. This instance will be used later in the code to analyze the sentiment of news headlines and assign sentiment scores to them.

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
            "publishedAt": article.get("publishedAt", ""),
        })

    return results