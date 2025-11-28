import os
import json
from datetime import datetime
import streamlit as st
from llm_utils import flashcards_via_llm
from storage_utils import FLASHCARDS_DIR, save_json, load_json_or_default

def render_flashcards_page(plan_store):
    st.markdown("## 🧠 Flashcards")
    st.caption("Generate active-recall flashcards based on your plan topics or any custom topic.")

    topics_opts = (
        [t["topic"] for t in (plan_store.get("plan", [{}])[0].get("tasks", []) or [])]
        if plan_store.get("plan")
        else []
    )

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            topic = st.text_input(
                "Topic",
                value=(topics_opts[0] if topics_opts else ""),
                placeholder="Enter a subject like: Software Engineering",
            )

        with col2:
            n = st.number_input(
                "How many cards?",
                min_value=2,
                max_value=40,
                value=8,
                help="More cards = more coverage, but longer review sessions.",
            )

        if st.button("⚡ Generate Flashcards", use_container_width=True):
            if not topic.strip():
                st.warning("Please enter a topic first.")
            else:
                cards = flashcards_via_llm(topic, int(n))
                fname = os.path.join(
                    FLASHCARDS_DIR,
                    f"flashcards_{topic.replace(' ','_')}_{int(datetime.utcnow().timestamp())}.json",
                )
                save_json(fname, cards)
                st.session_state["latest_flashcards"] = cards
                st.success(f"Generated {len(cards)} flashcards for **{topic}**!")

    if st.session_state.get("latest_flashcards"):
        st.markdown("---")
        st.subheader("Latest Flashcards")

        for i, c in enumerate(st.session_state["latest_flashcards"]):
            with st.expander(f"Q{i+1}: {c.get('question')}", expanded=False):
                st.markdown(f"**Answer:** {c.get('answer', '—')}")

        st.download_button(
            "⬇ Download Flashcards",
            data=json.dumps(st.session_state["latest_flashcards"], indent=2),
            file_name="flashcards.json",
            mime="application/json",
        )
    else:
        st.markdown("---")
        st.info("No flashcards yet. Generate some using the form above.")

    st.markdown("---")
    st.subheader("📁 Saved Flashcards")

    files = [f for f in os.listdir(FLASHCARDS_DIR) if f.endswith(".json")]
    if not files:
        st.caption("No saved flashcards found.")
    else:
        for f in files:
            if st.button(f"Load {f}", key=f):
                cards = load_json_or_default(os.path.join(FLASHCARDS_DIR, f), [])
                st.session_state["latest_flashcards"] = cards
                st.success(f"Loaded flashcards from {f}")