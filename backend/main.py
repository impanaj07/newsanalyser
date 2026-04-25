from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel  # ✅ ADD THIS
from services.auth import (
    register_user, authenticate_user, create_access_token, 
    get_current_user, users_db
)
from services.fetch import fetch_headlines, deduplication
from services.summary import get_summary
from services.sentiment import analyze_sentiment
from services.entities import extract_entities

app = FastAPI()


# ✅ NEW: request model for register
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@app.get("/")
def home():
    return {"message": "News Sentiment API running 🚀"}


# ✅ FIXED: accept JSON body instead of query params
@app.post("/register")
def register(data: RegisterRequest):
    result = register_user(data.username, data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user},
        expires_delta=None
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/analyze")
def analyze(topic: str, current_user: str = Depends(get_current_user)):
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


@app.get("/users")
def get_users(current_user: str = Depends(get_current_user)):
    return {"users": list(users_db.keys())}