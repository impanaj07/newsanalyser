from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def get_summary(topic: str, results: list[dict]) -> str:
    headlines_text = "\n".join(
        [f"- [{r['label']}] {r['headline']} ({r['source']})" for r in results]
    )

    prompt = f"""Here are {len(results)} news headlines about `{topic}`:
{headlines_text}

Summarize sentiment, themes, and patterns in 4-6 sentences."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content