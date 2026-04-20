from fastapi import FastAPI
from services.fetch import fetch_headlines, deduplication
from services.summary import get_summary
from services.sentiment import analyze_sentiment
from services.entities import extract_entities
app = FastAPI() 
@app.get("/")
def home():
    return {"message": "News Sentiment API running 🚀"}

@app.get("/analyze")
def analyze(topic: str):
    articles = fetch_headlines(topic)

    if not articles:
        return {"error": "No articles found"}

    articles = deduplication(articles)
    results = analyze_sentiment(articles)
    results, entity_counts = extract_entities(results)
    summary = get_summary(topic, results)

    return {
        "topic": topic,
        "results": results,
        "entities": dict(entity_counts.most_common(10)),
        "summary": summary
    }