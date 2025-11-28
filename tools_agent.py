# tools_agent.py — StudySage AI Coach with Tavily + LLM
import os
import re
from datetime import date, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from langchain_core.runnables import RunnableLambda
from langchain_community.tools.tavily_search import TavilySearchResults
from study_plan_utils import parse_syllabus_simple, build_study_plan
from storage_utils import PLAN_FILE, save_json
from llm_utils import get_llm_for_model  # ✅ only import this, not TAVILY_API_KEY

# -------- Tavily setup --------
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_tool: Optional[TavilySearchResults] = None
if TAVILY_API_KEY and TAVILY_API_KEY.strip():
    tavily_tool = TavilySearchResults(max_results=5)

# -------- Helper functions --------
def extract_details(text: str):
    """Extract days, hours, and clean topic list from the user's message."""
    days = 7
    hours = 2.0
    topics: List[str] = ["General revision"]

    # days
    d_match = re.search(r"(\d+)\s*days?", text, re.IGNORECASE)
    if d_match:
        days = int(d_match.group(1))

    # hours
    h_match = re.search(r"(\d+(\.\d+)?)\s*hours?", text, re.IGNORECASE)
    if h_match:
        hours = float(h_match.group(1))

    # explicit focus topics
    t_match = re.search(r"focus (more )?on (.+)", text, re.IGNORECASE)
    if t_match:
        topics_raw = t_match.group(2)
        topics_raw = re.sub(
            r"\d+(\.\d+)?\s*hours?/day\.?", "", topics_raw, flags=re.IGNORECASE
        )
        pieces = re.split(r",| and ", topics_raw, flags=re.IGNORECASE)
        topics = [p.strip(" .") for p in pieces if p.strip()]
        if not topics:
            topics = ["General revision"]
    return days, hours, topics

def guess_subject(text: str) -> Optional[str]:
    """Try to guess subject name from phrases like 'Software Engineering exam'."""
    m = re.search(r"(?:have|for)\s+([A-Za-z &+/]+?)\s+exam", text, re.IGNORECASE)
    if m:
        return m.group(1).strip(" .")
    return None

def expand_subject_to_topics(subject: str, n: int = 8) -> List[str]:
    """
    Use Tavily web search + the selected LLM to expand a subject name
    into a list of main syllabus topics.
    """
    selected = st.session_state.get("selected_model", "gpt-4o")
    llm = get_llm_for_model(selected)

    # 1) Web search via Tavily (if available)
    search_context = ""
    if tavily_tool is not None:
        try:
            results = tavily_tool.run(
                f"{subject} university exam syllabus main topics"
            )
            if isinstance(results, str):
                search_context = results
            elif isinstance(results, list):
                chunks = []
                for r in results:
                    if isinstance(r, dict):
                        chunks.append(
                            r.get("content")
                            or r.get("snippet")
                            or r.get("summary")
                            or ""
                        )
                search_context = "\n\n".join(chunks)
        except Exception:
            search_context = ""

    # 2) No LLM → fallback topics
    if llm is None:
        if search_context:
            lines = [l.strip(" -•\t") for l in search_context.splitlines() if l.strip()]
            return lines[:n] or [f"Unit {i+1} of {subject}" for i in range(n)]
        return [f"Unit {i+1} of {subject}" for i in range(n)]

    # 3) Ask LLM to convert search context into topic list
    if search_context:
        prompt = (
            f"You are an exam coach. Based on the subject '{subject}' and "
            "the following web search results about its university exam syllabus, "
            f"list the {n} most important exam topics.\n\n"
            f"{search_context[:4000]}\n\n"
            "Return one topic per line, no numbering or bullets."
        )
    else:
        prompt = (
            f"List {n} main exam-focused topics for the subject '{subject}'. "
            "Return one topic per line, without bullets or numbering."
        )

    try:
        resp = llm.invoke(prompt)
        text = getattr(resp, "content", str(resp))
        lines = [l.strip(" -•\t") for l in text.splitlines() if l.strip()]
        topics = lines[:n]
        return topics or [subject]
    except Exception:
        return [f"Unit {i+1} of {subject}" for i in range(n)]

# -------- Main agent logic --------
def ai_agent(user_input: str) -> Dict:
    """Main Study Coach logic: parse → maybe expand subject → build & save plan."""
    days, hours, topics = extract_details(user_input)

    # If we only have 'General revision', try to infer subject & expand
    if topics == ["General revision"]:
        subject = guess_subject(user_input)
        if subject:
            topics = expand_subject_to_topics(subject, n=8)

    today = date.today()
    end_date = today + timedelta(days=days - 1)

    syllabus_text = "\n".join(topics)
    parsed_topics = parse_syllabus_simple(syllabus_text)

    plan = build_study_plan(
        parsed_topics,
        today.isoformat(),
        end_date.isoformat(),
        hours,
    )

    save_json(PLAN_FILE, plan)
    st.session_state["last_plan"] = plan

    topic_preview = ", ".join(topics[:6])
    if len(topics) > 6:
        topic_preview += ", ..."

    return {
        "message": f"📚 {days}-Day Study Plan Created ({hours} hrs/day)",
        "preview": f"Topics: {topic_preview}",
    }
study_sage_executor = RunnableLambda(ai_agent)