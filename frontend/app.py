import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Backend URL
API_URL = "http://127.0.0.1:8000/analyze"

MAX_TOPIC_LENGTH = 100
MIN_TOPIC_LENGTH = 2

#input validation and error handling
def validate_topic(topic: str) -> tuple[bool, str]:
    if not topic or topic.strip() == "":
        return False, "Please enter a topic before analyzing."
    if len(topic.strip()) < MIN_TOPIC_LENGTH:
        return False, f" Topic is too short. Please enter at least {MIN_TOPIC_LENGTH} characters."
    if len(topic.strip()) > MAX_TOPIC_LENGTH:
        return False, f" Topic is too long. Please keep it under {MAX_TOPIC_LENGTH} characters (you entered {len(topic.strip())})."
    if topic.strip().replace(" ", "").isdigit():
        return False, "Topic cannot be numbers only. Please enter a meaningful topic."
    return True, ""
 
#api call with error handling
def fetch_analysis(topic:str)->tuple[dict | None,str]:
    try:
        response=requests.get(API_URL, params={"topic": topic.strip()}, timeout=30)
        if response.status_code==422:
            return None, "Invalid request sent to backend.Please try a different topic"
        if response.status_code==429:
            return None,"Too many requests.Please wait a momentnand try again"
        if response.status_code==500:
            return None, "Backend server error.Please try again later"
        if response.status_code!=200:
            return None, f"Unexpected error: {response.status_code}. Please try again later."
        data=response.json()
        return data, ""
    except requests.exceptions.ConnectionError:
        return None, " Cannot connect to the backend. Make sure the FastAPI server is running (`uvicorn main:app --reload`)."
 
    except requests.exceptions.Timeout:
        return None, " Request timed out. The backend is taking too long — please try again."
 
    except requests.exceptions.JSONDecodeError:
        return None, "Backend returned an invalid response. Please try again."
 
    except Exception as e:
        return None, f" Unexpected error: {str(e)}"

st.set_page_config(
    page_title="News Sentiment Analyzer",
    layout="wide"
)

# Title
st.title("📰 News Sentiment Analyzer")
st.markdown("Analyze real-time news sentiment, entities, and trends")

# Sidebar
st.sidebar.header("⚙️ Controls")
topic = st.sidebar.text_input("Enter Topic", "artificial intelligence")

analyze_btn = st.sidebar.button("🚀 Analyze")

# Main Logic
if analyze_btn:
    # Validate topic
    is_valid, error_msg = validate_topic(topic)
    if not is_valid:
        st.error(error_msg)
        st.stop()

    with st.spinner("Fetching and analyzing news..."):
        data, error_msg = fetch_analysis(topic)
        if data is None:
            st.error(error_msg)
            st.stop()

    if "error" in data:
        st.error(data["error"])
        st.stop()

    results = pd.DataFrame(data["results"])

    # 📊 Sentiment Distribution
    st.subheader("📊 Sentiment Distribution")

    fig = px.pie(
        results,
        names="label",
        title=f"Sentiment for '{topic}'",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    # 🔍 Filter
    st.subheader("🔍 Filter Headlines")

    sentiment_filter = st.selectbox(
        "Select Sentiment",
        ["All", "Positive 😊", "Neutral 😐", "Negative 😟"]
    )

    if sentiment_filter != "All":
        filtered = results[results["label"] == sentiment_filter]
    else:
        filtered = results

    # 🗞 Headlines
    st.subheader("🗞 Headlines")

    for _, row in filtered.iterrows():
        published_at = ""
        if row['publishedAt']:
            try:
                dt = datetime.fromisoformat(row['publishedAt'].replace('Z', '+00:00'))
                published_at = dt.strftime('%Y-%m-%d %H:%M UTC')
            except:
                published_at = row['publishedAt']
        else:
            published_at = "Unknown"

        st.markdown(f"""
        ### {row['headline']}
        **Source:** {row['source']}  
        **Sentiment:** {row['label']}  
        **Published:** {published_at}

        🔗 [Read full article]({row['url']})
        """)
        st.markdown("---")

    # 🏷 Entities
    st.subheader("🏷 Top Entities")

    entities = data["entities"]

    if entities:
        entity_df = pd.DataFrame(
            entities.items(),
            columns=["Entity", "Mentions"]
        )

        fig2 = px.bar(
            entity_df,
            x="Entity",
            y="Mentions",
            title="Most Mentioned Entities"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No entities found.")

    # 🤖 Summary
    st.subheader("🤖 AI Summary")
    st.info(data["summary"])

else:
    st.info("👈 Enter a topic and click Analyze")