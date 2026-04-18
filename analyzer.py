import os #imports the os module for interacting with the operating system
import requests #imports the requests module for making HTTP requests
import json #imports the json module for working with JSON data that is used for parsing and generating json data
import matplotlib.pyplot as plt #imports the pyplot module from matplotlib for creating visualizations
import matplotlib.patches as patches #imports the patches module from matplotlib for creating custome legend patches
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer #imports the SentimentIntensityAnalyzer class from the vaderSentiment module for performing sentiment analysis
from groq import Groq
from datetime import datetime 

NEWS_API_KEY="YOUR_NEWS_API_KEY" #retrieves the NEWS_API_KEY from the environment variables #retrieves the Gemini_API_KEY from the environment variables

def fetch_headlines(topic:str, num:int=25)->list[dict]:#defines a function called fetch_headlines that takes a topic and an optional number of headlines to fetch, and returns a list of dictionaries containing the headlines and their corresponding sentiment scores
    print(f"\n Fetching headlines for the `{topic}`..")#prints a message indicating that the function is fetching headlines for the specified topic
    url="https://newsapi.org/v2/everything" #sets the URL for the News API endpoint to fetch news articles
    params={
        "q":topic,#sets the query parameter to the specified topic to search for relevant news articles
        "language":"en",#sets the language parameter to English to filter the news articles to only those written in English
        "sortBy":"publishedAt",#sets the sortBy parameter to publishedAt to sort the news articles by their publication date, with the most recent articles appearing first
        "pageSize":num,#sets the pageSize parameter to the specified number of headlines to fetch, which limits the number of news articles returned by the API to the specified number
        "apiKey":NEWS_API_KEY,#sets the apiKey parameter to the NEWS_API_KEY retrieved from the environment variables, which is required to authenticate the API request and access the news data
    }
    response=requests.get(url,params=params)
    response.raise_for_status() #raises an exception if the HTTP request returned an unsuccessful status code
    data=response.json()#parses the JSON response from the API into a Python dictionary using the json() method of the response object
    articles=data.get("articles",[])#retrieves the list of articles from the parsed JSON data using the get() method, which returns an empty list if the "articles" key is not found in the data. Each article is represented as a dictionary containing information such as the headline, source, publication date, and URL.
    if not articles:
        print("No articles found.Try a different topic.")
        return []
    print(f"Fetched {len(articles)} articles.")
    return articles

def analyze_sentiment(articles: list[dict])->list[dict]:
    print("\n Running sentiment analysis...")
    analyzer=SentimentIntensityAnalyzer() #creates an instance of the SentimentIntensityAnalyzer class
    results=[]
    for article in articles:
        headline=article.get("title","") #retrieves the headline of the article using the get() method, which returns an empty string if the "title" key is not found in the article dictionary
        if not headline or headline=="[Removed]":
            continue
        scores=analyzer.polarity_scores(headline) #calculates the sentiment scores for the headline using the polarity_scores method of the SentimentIntensityAnalyzer instance
        compound=scores["compound"]
        if compound >= 0.05:
            label = "Positive 😊"
        elif compound <= -0.05:
            label = "Negative 😟"
        else:
            label = "Neutral 😐"
        results.append({
            "headline":headline,
            "source":article.get("source",{}).get("name","Unknown"),
            "compound":compound,
            "label":label,
            "url":article.get("url",""),
        })
    print(f"Analyzed sentiment for {len(results)} headlines.")
    return results

def print_results_table(results: list[dict]):
    print("\n" + "═" * 90)
    print(f"{'HEADLINE':<55} {'SOURCE':<18} {'SCORE':>6}  {'SENTIMENT'}")
    print("═" * 90)
 
    for r in results:
        headline = r["headline"][:52] + "..." if len(r["headline"]) > 52 else r["headline"]
        print(f"{headline:<55} {r['source']:<18} {r['compound']:>+.3f}  {r['label']}")
 
    print("═" * 90)


def get_summary(topic: str, results: list[dict]) -> str:
    print("\n Generating summary using Groq...")

    client = Groq(api_key="YOUR_GROQ_API_KEY")

    headlines_text = "\n".join(
        [f"- [{r['label']}] {r['headline']} ({r['source']})" for r in results]
    )

    prompt = f"""Here are {len(results)} news headlines about `{topic}` with their sentiment labels:
{headlines_text}

Please provide:
1. **Overall Sentiment**: What is the general tone of the news about this topic?
2. **Key Themes**: What are the 2-3 main topics or events being discussed?
3. **Notable Patterns**: Any interesting patterns — e.g., is coverage polarized, is sentiment shifting?

Keep your response concise — 4 to 6 sentences max."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content

def visualize_sentiment(topic:str,results:list[dict],summary:str):
    print("\n Generating visualizations...")
    plt.close("all")
    counts={"Positive 😊": 0, "Neutral 😐": 0, "Negative 😟": 0}
    for r in results:
        counts[r["label"]]+=1
    labels=list(counts.keys())
    values=list(counts.values())
    colors = ["#4ade80", "#94a3b8", "#f87171"]
    fig, (ax1,ax2)=plt.subplots(1,2,figsize=(14,6))
    fig.patch.set_facecolor("#0f172a")
    bars=ax1.bar(labels,values,color=colors,edgecolor="#1e293b",linewidth=1.5,width=0.5)
    ax1.set_facecolor("#1e293b")
    ax1.set_title(f"Sentiment Distribution\n\"{topic}\"", color="white", fontsize=13, pad=15)
    ax1.set_ylabel("Number of Headlines", color="#94a3b8")
    ax1.tick_params(colors="white")
    ax1.spines[:].set_color("#334155")
    for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                      str(val), ha="center", color="white", fontsize=12, fontweight="bold")
    ax2.set_facecolor("#1e293b")
    ax2.axis("off")
    ax2.set_title("🤖 Groq's AI Summary", color="white", fontsize=13, pad=15)
 
    # Wrap text
    import textwrap
    wrapped = textwrap.fill(summary, width=55)
    ax2.text(0.05, 0.85, wrapped, transform=ax2.transAxes,
             fontsize=9.5, color="#e2e8f0", verticalalignment="top",
             wrap=True, bbox=dict(facecolor="#0f172a", edgecolor="#334155",
                                  boxstyle="round,pad=0.8", alpha=0.9))
 
    # Footer
    fig.text(0.5, 0.01,
             f"Generated on {datetime.now().strftime('%d %b %Y %H:%M')} · Powered by NewsAPI + Gemini",
             ha="center", color="#475569", fontsize=8)
 
    plt.tight_layout(pad=2.5)
    filename = f"sentiment_{topic.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✅ Chart saved as '{filename}'")
    plt.show()
 
def main():
 
    topic = input("\n🔎 Enter a topic to analyze (e.g. 'AI', 'cricket', 'climate'): ").strip()
    if not topic:
        topic = "artificial intelligence"
 
    # Stage 1: Fetch
    articles = fetch_headlines(topic, num=25)
    if not articles:
        return
 
    # Stage 2: Sentiment
    results = analyze_sentiment(articles)
    print_results_table(results)
 
    # Stage 3: AI Summary
    ai_summary = get_summary(topic, results)
    print("\n🤖 Gemini says:")
    print("─" * 60)
    print(ai_summary)
    print("─" * 60)
 
    # Stage 4: Visualize
    visualize_sentiment(topic, results, ai_summary)
 
    # Optional: Save to CSV
    save = input("\n💾 Save results to CSV? (y/n): ").strip().lower()
    if save == "y":
        import csv
        filename = f"results_{topic.replace(' ', '_')}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["headline", "source", "compound", "label", "url"])
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Saved to '{filename}'")
 
    print("\n✨ Done! Great work.")
 
 
if __name__ == "__main__":
    main()

        

