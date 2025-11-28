import json
from datetime import date, timedelta

import streamlit as st
import pandas as pd

from study_plan_utils import parse_syllabus_simple, build_study_plan
from storage_utils import PLAN_FILE, save_json


def render_planner(plan_store):
    st.markdown("## 🗓 Planner")
    st.caption("Paste your syllabus or upload a text file — I’ll generate a structured plan based on the time available.")

    tab_create, tab_current = st.tabs(["🧩 Create / Update Plan", "📋 Current Plan"])

    with tab_create:
        # Input Card
        with st.container():
            st.markdown(
                """
                <div style="padding:1rem; border-radius:0.8rem;
                            background-color:#FFFFFF;
                            box-shadow:0 4px 16px rgba(0,0,0,0.05);">
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 1])
            syllabus_text = ""

            with col1:
                syllabus_text = st.text_area(
                    "Syllabus (one topic per line)",
                    height=200,
                    placeholder="Example:\nUnit 1: Basics\nUnit 2: ML Models\nUnit 3: Neural Networks\n...",
                )
                uploaded = st.file_uploader("Upload .txt file", type=["txt"])
                if uploaded:
                    try:
                        syllabus_text = uploaded.getvalue().decode("utf-8")
                    except Exception:
                        syllabus_text = str(uploaded.getvalue())

            with col2:
                st.markdown("#### Quick actions")
                if st.button("📌 Load Sample"):
                    syllabus_text = (
                        "Intro to AI\nML Basics\nNeural Networks\nOptimization\nProjects & Practice"
                    )
                    st.session_state["syllabus_temp"] = syllabus_text

                st.markdown(
                    """
                    <small>Use this sample if you just want to try out the planner.</small>
                    """,
                    unsafe_allow_html=True,
                )

            # Update text if Sample button was pressed
            if "syllabus_temp" in st.session_state:
                syllabus_text = st.session_state["syllabus_temp"]

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        if syllabus_text:
            topics = parse_syllabus_simple(syllabus_text)
            st.subheader("🧾 Parsed Topics")
            st.table(pd.DataFrame(topics))

            st.subheader("⚙️ Plan Settings")
            colA, colB, colC = st.columns(3)
            with colA:
                start_date_val = st.date_input("Start date", value=date.today())
            with colB:
                end_date_val = st.date_input("End date", value=date.today() + timedelta(days=13))
            with colC:
                daily_hours = st.slider("Daily hours", 0.5, 8.0, 2.0, step=0.5)

            pomodoro_mins = st.selectbox("Pomodoro length (minutes)", [15, 20, 25, 30, 50], index=2)

            if st.button("✨ Generate & Save Plan", use_container_width=True):
                if end_date_val < start_date_val:
                    st.error("End date must be on or after the start date.")
                else:
                    plan = build_study_plan(
                        topics,
                        start_date_val.isoformat(),
                        end_date_val.isoformat(),
                        daily_hours,
                        pomodoro_mins,
                    )
                    save_json(PLAN_FILE, plan)
                    st.success("🎯 Study plan created successfully!")
                    st.rerun()  # <-- updated here

        else:
            st.info("Paste your syllabus or upload a .txt file to start planning.")

    with tab_current:
        if plan_store:
            st.subheader("📋 Current Plan")
            st.caption(f"Generated at: {plan_store.get('meta', {}).get('created_at', 'unknown')}")

            rows = []
            for day in plan_store.get("plan", [])[:21]:
                for idx, task in enumerate(day["tasks"]):
                    rows.append(
                        {
                            "Date": day["date"],
                            "Block": idx + 1,
                            "Topic": task["topic"],
                            "Minutes": task["pomodoro_minutes"],
                            "Activity": task["activity"],
                        }
                    )

            if rows:
                st.dataframe(pd.DataFrame(rows))
            else:
                st.info("Plan exists but no tasks found.")

            st.download_button(
                "⬇ Download Full Plan",
                data=json.dumps(plan_store, indent=2),
                file_name="study_plan.json",
                mime="application/json",
            )
        else:
            st.info("No plan found yet. Create one in the **Create / Update Plan** tab.")
