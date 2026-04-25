import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Backend URL
API_URL = "http://127.0.0.1:8000"
BACKEND_ANALYZE_URL = "http://127.0.0.1:8000/analyze"

MAX_TOPIC_LENGTH = 100
MIN_TOPIC_LENGTH = 2

# Initialize session state for authentication
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication functions
def register(username: str, email: str, password: str) -> tuple[bool, str]:
    try:
        response = requests.post(
            f"{API_URL}/register",
            json={"username": username, "email": email, "password": password},  # FIXED
            timeout=10
        )
        if response.status_code == 200:
            return True, "Registration successful! Please login."
        else:
            try:
                data = response.json()
                return False, data.get("detail", "Registration failed")
            except Exception:
                return False, f"Registration failed: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def login(username: str, password: str) -> tuple[bool, str]:
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            st.session_state.authenticated = True
            return True, "Login successful!"
        else:
            try:
                data = response.json()
                return False, data.get("detail", "Invalid username or password")
            except Exception:
                return False, f"Login failed: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.authenticated = False
    st.rerun()

# Input validation
def validate_topic(topic: str) -> tuple[bool, str]:
    if not topic or topic.strip() == "":
        return False, "Please enter a topic before analyzing."
    if len(topic.strip()) < MIN_TOPIC_LENGTH:
        return False, f"Topic is too short. Please enter at least {MIN_TOPIC_LENGTH} characters."
    if len(topic.strip()) > MAX_TOPIC_LENGTH:
        return False, f"Topic is too long. Please keep it under {MAX_TOPIC_LENGTH} characters."
    if topic.strip().replace(" ", "").isdigit():
        return False, "Topic cannot be numbers only."
    return True, ""

# API call
def fetch_analysis(topic: str) -> tuple[dict | None, str]:
    if not st.session_state.token:
        return None, "Please login to analyze news."
    
    try:
        response = requests.get(
            BACKEND_ANALYZE_URL,
            params={"topic": topic.strip()},
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=30
        )

        if response.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.token = None
            return None, "Session expired. Please login again."
        if response.status_code == 422:
            return None, "Invalid request sent to backend."
        if response.status_code == 429:
            return None, "Too many requests. Please wait a moment and try again"  # FIXED
        if response.status_code == 500:
            return None, "Backend server error."
        if response.status_code != 200:
            return None, f"Unexpected error: {response.status_code}"

        return response.json(), ""

    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend. Is FastAPI running?"
    except requests.exceptions.Timeout:
        return None, "Request timed out."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Page config
st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")

# Sidebar Authentication
st.sidebar.header("🔐 Authentication")

if not st.session_state.authenticated:
    auth_tab = st.sidebar.tabs(["Login", "Register"])

    with auth_tab[0]:
        login_user = st.text_input("Username")
        login_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = login(login_user, login_pass)
            if success:
                st.success(msg)
                st.rerun()  # Updated from experimental_rerun
            else:
                st.error(msg)

    with auth_tab[1]:
        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_pass2 = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if reg_pass != reg_pass2:
                st.error("Passwords do not match")
            else:
                success, msg = register(reg_user, reg_email, reg_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()

# Main UI
st.title("📰 News Sentiment Analyzer")

topic = st.sidebar.text_input("Enter Topic", "artificial intelligence")
analyze_btn = st.sidebar.button("🚀 Analyze")

if analyze_btn:
    if not st.session_state.authenticated:
        st.error("Please login first")
        st.stop()

    valid, msg = validate_topic(topic)
    if not valid:
        st.error(msg)
        st.stop()

    with st.spinner("Analyzing..."):
        data, err = fetch_analysis(topic)
        if not data:
            st.error(err)
            st.stop()

    if "error" in data:
        st.error(data["error"])
        st.stop()

    results = pd.DataFrame(data["results"])

    # Pie chart
    st.subheader("📊 Sentiment Distribution")
    fig = px.pie(results, names="label", hole=0.4)
    st.plotly_chart(fig)

    # Filter (FIXED)
    sentiment_filter = st.selectbox(
        "Filter",
        ["All", "Positive", "Neutral", "Negative"]
    )

    if sentiment_filter != "All":
        results = results[results["label"] == sentiment_filter]

    # Headlines
    st.subheader("🗞 Headlines")
    for _, row in results.iterrows():
        st.markdown(f"### {row['headline']}")
        st.markdown(f"**Sentiment:** {row['label']}")
        st.markdown(f"[Read more]({row['url']})")
        st.markdown("---")

    # Entities
    st.subheader("🏷 Entities")
    entity_df = pd.DataFrame(data["entities"].items(), columns=["Entity", "Count"])
    st.bar_chart(entity_df.set_index("Entity"))

    # Summary
    st.subheader("🤖 Summary")
    st.info(data["summary"])

else:
    st.info("Enter a topic and click Analyze")