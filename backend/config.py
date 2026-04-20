import os
from dotenv import load_dotenv
import spacy

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

nlp = spacy.load("en_core_web_sm")