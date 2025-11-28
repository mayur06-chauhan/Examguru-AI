# ui_pages/settings_page.py
import streamlit as st
from llm_utils import MODEL_OPTIONS, GEMINI_API_KEY
from storage_utils import PLAN_FILE, PROGRESS_FILE, FLASHCARDS_DIR

def render_settings_page():
    st.markdown("## ⚙️ Settings")
    st.caption("Configure ExamGuru AI settings and check API key status.")

    st.subheader("🧠 AI Model")
    selected_model = st.selectbox(
        "Choose model",
        options=MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(st.session_state.get("selected_model", MODEL_OPTIONS[0])),
    )
    st.session_state.selected_model = selected_model

    st.markdown("---")
    st.subheader("🔑 API Key Status")

    if GEMINI_API_KEY:
        st.success("Gemini API key detected!")
    else:
        st.error("❌ Missing: `GEMINI_API_KEY` — set it in your environment")

    st.markdown("---")
    st.subheader("💾 Storage Files")
    st.caption(f"Plan: `{PLAN_FILE}`")
    st.caption(f"Progress: `{PROGRESS_FILE}`")
    st.caption(f"Flashcards folder: `{FLASHCARDS_DIR}`")