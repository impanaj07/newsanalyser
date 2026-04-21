import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Backend URL
API_URL = "http://127.0.0.1:8000/analyze"

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

    with st.spinner("Fetching and analyzing news..."):
        try:
            response = requests.get(API_URL, params={"topic": topic})
            data = response.json()
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
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
        st.markdown(f"""
        ### {row['headline']}
        **Source:** {row['source']}  
        **Sentiment:** {row['label']}  

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