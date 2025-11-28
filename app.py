import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd  # used inside some pages indirectly (safe to keep)

from tools_agent import study_sage_executor
from storage_utils import load_json_or_default, PLAN_FILE, PROGRESS_FILE
from llm_utils import MODEL_OPTIONS

from ui_pages.ai_coach_chat_page import render_ai_coach_chat
from ui_pages.planner_page import render_planner
from ui_pages.flashcards_page import render_flashcards_page
from ui_pages.progress_page import render_progress_page
from ui_pages.dashboard_page import render_dashboard_page
from ui_pages.settings_page import render_settings_page

# ------------------ Streamlit Config ------------------
st.set_page_config(page_title="ExamGuru AI", layout="wide")

# ---------------- Sidebar UI ----------------
st.sidebar.title("🎓 ExamGuru AI")
st.sidebar.caption("Your AI-powered exam coach")

st.sidebar.markdown("### 📌 Navigation")

page = st.sidebar.radio(
    "",
    [
        "🤖 AI Coach Chat",
        "🗓 Planner",
        "🧠 Flashcards",
        "✅ Progress",
        "📊 Dashboard",
        "⚙️ Settings",
    ],
)

# Display the uploaded image (path provided by user)
st.sidebar.markdown("### Visual")
uploaded_image_path = "/mnt/data/80928960-6379-41b0-93f2-b49a6fb7400f.png"
if os.path.exists(uploaded_image_path):
    st.sidebar.image(uploaded_image_path, use_column_width=True)
else:
    st.sidebar.info("No uploaded image found at expected path.")

st.sidebar.markdown("---")
st.sidebar.caption("Tip: Configure your API keys in **Settings** first.")

# ---------------- Load persisted data ----------------
plan_store: dict = load_json_or_default(PLAN_FILE, {})
progress_store: dict = load_json_or_default(PROGRESS_FILE, {"entries": []})

# Initialize selected model in session_state if needed
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.5-flash"

# ---------------- Page Routing ----------------
def route_pages():
    if page == "🤖 AI Coach Chat":
        render_ai_coach_chat(study_sage_executor)
    elif page == "🗓 Planner":
        render_planner(plan_store)
    elif page == "🧠 Flashcards":
        render_flashcards_page(plan_store)
    elif page == "✅ Progress":
        render_progress_page(plan_store, progress_store)
    elif page == "📊 Dashboard":
        render_dashboard_page(plan_store, progress_store)
    elif page == "⚙️ Settings":
        render_settings_page()
route_pages()
