from datetime import date, datetime
import streamlit as st
import pandas as pd
from study_plan_utils import adapt_plan_basic
from storage_utils import PLAN_FILE, PROGRESS_FILE, save_json

def render_progress_page(plan_store, progress_store):
    st.markdown("## ✅ Progress")
    st.caption("Update what you completed today & score yourself — your plan adapts if needed!")

    if not plan_store:
        st.info("No plan yet — please create one in the **Planner** page.")
        return

    tab_today, tab_history = st.tabs(["📝 Submit Progress", "📜 Progress History"])

    with tab_today:
        st.markdown("---")

        prog_date = st.date_input("Progress date", value=date.today())

        # Get planned tasks for selected date
        day_plan = next(
            (d for d in plan_store.get("plan", []) if d["date"] == prog_date.isoformat()),
            None,
        )

        if day_plan:
            options = [f"{i}. {t['topic']}" for i, t in enumerate(day_plan["tasks"])]
            selected = st.multiselect(
                "Select tasks completed today",
                options,
                help="Pick all blocks you completed.",
            )
            completed_list = [int(s.split(".")[0]) for s in selected]
        else:
            st.warning("No tasks scheduled for this date in the plan.")
            completed_list = []

        assess_topic = st.selectbox(
            "Self-assess topic",
            options=sorted({task["topic"] for day in plan_store["plan"] for task in day["tasks"]}),
        )
        assess_score = st.slider("Self-assessment (1 Weak — 5 Strong)", 1, 5, 4)

        if st.button("📌 Submit Progress", use_container_width=True):
            entry = {
                "date": prog_date.isoformat(),
                "completed_tasks": completed_list,
                "self_assessment": {"topic": assess_topic, "score": assess_score},
                "created_at": datetime.utcnow().isoformat(),
            }

            progress_store.setdefault("entries", []).append(entry)
            save_json(PROGRESS_FILE, progress_store)

            note = "Progress saved!"
            if assess_score < 3:
                adapted = adapt_plan_basic(plan_store, assess_topic, assess_score)
                save_json(PLAN_FILE, adapted)
                note += " 📌 Extra review added for weak topic."

            st.success(note)
            st.rerun()

    with tab_history:
        st.markdown("---")
        entries = progress_store.get("entries", [])
        if entries:
            df = pd.DataFrame(entries)
            st.dataframe(df)
        else:
            st.info("No progress submitted yet.")