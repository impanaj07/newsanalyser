# 📰 News Sentiment Analyzer

A full-stack AI-powered news analysis tool that fetches real-time headlines, performs sentiment analysis, extracts named entities, and generates AI-powered summaries.

Built as a learning project covering Data Science, NLP, and GenAI — evolving from a terminal script to a full-stack web application.

---

## 🚀 Live Demo

> Coming soon — deployment in progress

---

## 🖼️ Screenshot

> Add a screenshot of your Streamlit UI here

---

## ✨ Features

- 📡 **Real-time News Fetching** — pulls latest headlines from NewsAPI for any topic
- 🧹 **Deduplication** — removes near-duplicate headlines using fuzzy string matching
- 🔍 **Sentiment Analysis** — classifies each headline as Positive, Negative, or Neutral using VADER
- 🏷️ **Named Entity Recognition** — extracts people, places, organizations, and events using spaCy
- 🤖 **AI Summary** — generates an insightful summary using Groq (LLaMA 3.3 70B)
- 📊 **Interactive Charts** — sentiment distribution and entity frequency charts via Plotly
- 🔗 **Full-stack Architecture** — Streamlit frontend + FastAPI backend

---

## 🏗️ Project Structure

```
news/
├── backend/
│   ├── services/
│   │   ├── fetch.py          # NewsAPI integration
│   │   ├── sentiment.py      # VADER sentiment analysis
│   │   ├── entities.py       # spaCy NER extraction
│   │   └── summary.py        # Groq AI summary generation
│   ├── config.py             # API keys and configuration
│   └── main.py               # FastAPI app and routes
├── frontend/
│   └── app.py                # Streamlit UI
├── analyzer.py               # Original terminal version
├── .env                      # API keys (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Uvicorn |
| NLP | VADER Sentiment, spaCy |
| GenAI | Groq API (LLaMA 3.3 70B) |
| News Data | NewsAPI |
| Deduplication | RapidFuzz |
| Language | Python 3.10+ |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/news-sentiment-analyzer.git
cd news-sentiment-analyzer
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 5. Set up your API keys

Create a `.env` file in the root directory:
```
NEWS_API_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_key_here
```

Get your free API keys:
- **NewsAPI** → [newsapi.org](https://newsapi.org) (free tier)
- **Groq** → [console.groq.com](https://console.groq.com) (free tier)

---

## ▶️ Running the App

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1 — Start the FastAPI backend
```bash
cd backend
uvicorn main:app --reload
```
Backend runs at: `http://127.0.0.1:8000`

### Terminal 2 — Start the Streamlit frontend
```bash
cd frontend
streamlit run app.py
```
Frontend runs at: `http://localhost:8501`

---

## 🔌 API Reference

### `GET /analyze`

Analyzes news headlines for a given topic.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | ✅ | Topic to search for (e.g. `cricket`, `AI`) |

**Example Request:**
```
GET http://127.0.0.1:8000/analyze?topic=cricket
```

**Example Response:**
```json
{
  "results": [
    {
      "headline": "India beats Australia in final over thriller",
      "source": "ESPN",
      "compound": 0.52,
      "label": "Positive 😊",
      "entities": [
        {"text": "India", "label": "GPE", "icon": "🌍"},
        {"text": "Australia", "label": "GPE", "icon": "🌍"}
      ],
      "url": "https://..."
    }
  ],
  "entities": {
    "India": 5,
    "Virat Kohli": 3,
    "Mumbai": 2
  },
  "summary": "Coverage is predominantly positive..."
}
```

---

## 🧠 How It Works

```
User enters topic
       ↓
FastAPI backend receives request
       ↓
fetch.py → NewsAPI → 30 raw headlines
       ↓
Deduplication → remove near-duplicates (fuzzy match ≥ 85%)
       ↓
sentiment.py → VADER scores each headline
       ↓
entities.py → spaCy extracts PERSON, ORG, GPE, EVENT
       ↓
summary.py → Groq LLaMA summarizes all headlines
       ↓
FastAPI returns JSON response
       ↓
Streamlit renders charts, table, and summary
```

---

## 🗺️ Roadmap

- [x] Terminal version with sentiment analysis
- [x] Deduplication with fuzzy matching
- [x] Named Entity Recognition with spaCy
- [x] AI summary with Groq
- [x] Streamlit frontend
- [x] FastAPI backend
- [ ] SQLite database for search history
- [ ] Sentiment trend over time chart
- [ ] Deploy on Streamlit Cloud + Render
- [ ] Add tests with pytest
- [ ] Docker support

---

## 📈 Project Evolution

| Version | Description |
|---------|-------------|
| `analyzer.py` | Terminal script — fetch, sentiment, chart |
| v2 | Added deduplication + NER |
| Current | Full-stack — Streamlit + FastAPI |
| Next | Deployed + Database + Tests |

---

## 🙋 Author

**Impana J**
Built as a Data Science + GenAI learning project.

---

## 📄 License

MIT License — feel free to use and build on this project.
