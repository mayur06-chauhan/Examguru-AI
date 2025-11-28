# llm_utils.py
import os
from typing import List, Dict
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Only Gemini option
MODEL_OPTIONS = [
    "gemini-2.5-flash",
]

def get_llm_for_model(selected_model: str):
    """
    Instantiate the only supported model: Gemini.
    """
    if selected_model.startswith("gemini") and ChatGoogleGenerativeAI is not None:
        if GEMINI_API_KEY:
            try:
                return ChatGoogleGenerativeAI(
                    model=selected_model,
                    temperature=0.2,
                    google_api_key=GEMINI_API_KEY,
                )
            except Exception:
                return None
    return None

def flashcards_via_llm(topic: str, n: int = 8) -> List[Dict]:
    """
    Generate flashcards using only Gemini.
    """
    selected = st.session_state.get("selected_model", "gemini-2.5-flash")
    llm = get_llm_for_model(selected)

    # fallback if no key / no response
    if llm is None:
        return [
            {
                "question": f"Key question {i+1} about {topic}",
                "answer": "Answer in 1–2 sentences.",
            }
            for i in range(n)
        ]

    try:
        prompt = (
            f"Create {n} concise active-recall flashcards for the topic: {topic}.\n"
            "For each card, output exactly two lines:\n"
            "Q: <question>\n"
            "A: <short answer>\n"
            "Separate cards with a blank line."
        )

        resp = llm.invoke(prompt)
        text = getattr(resp, "content", str(resp))
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        cards: List[Dict] = []
        i = 0
        while i < len(lines) and len(cards) < n:
            if lines[i].lower().startswith("q:"):
                q = lines[i][2:].strip()
                answer = ""
                j = i + 1
                while j < len(lines) and not answer:
                    if lines[j].lower().startswith("a:"):
                        answer = lines[j][2:].strip()
                    j += 1
                if not answer:
                    answer = "Recall the key concept."
                cards.append({"question": q, "answer": answer})
                i = j
            else:
                i += 1

        if not cards:
            return [
                {"question": f"Key question {i+1}", "answer": "Short answer."}
                for i in range(n)
            ]
        return cards

    except Exception:
        return [
            {
                "question": f"Key question {i+1} about {topic}",
                "answer": "Answer in 1–2 sentences.",
            }
            for i in range(n)
        ]