import streamlit as st
import pandas as pd


def render_ai_coach_chat(study_sage_executor):
    # 🎓 Main Header at Top
    st.markdown("<h1 style='margin-bottom: -0.2rem;'>🎓 ExamGuru AI</h1>", unsafe_allow_html=True)
    st.caption("Ace your exams with smart planning.")

    # 💡 Branding tagline banner below header
    st.markdown(
        """
        <div style="padding:0.6rem 1rem; border-radius:0.8rem;
                    background-color:#EEF2FF; margin:0.8rem 0 1.2rem 0;">
            <span style="font-weight:600; color:#4F46E5;">
                Smart planning · Active recall · Progress tracking
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main input card UI
    with st.container():
        st.markdown(
            """
            <div style="padding:1.2rem; border-radius:1rem;
                        background-color:#FFFFFF;
                        box-shadow:0 4px 18px rgba(0,0,0,0.04);">
            """,
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([2.2, 1])

        with col_left:
            user_input = st.text_area(
                "Tell me about your exam:",
                height=160,
                placeholder=(
                    "Example: I have Software Engineering exam in 10 days, "
                    "3 hours/day; focus more on Testing and SDLC."
                ),
            )
        with col_right:
            st.markdown("##### Quick tips")
            st.markdown(
                """
                - Mention **exam name**  
                - Tell me **days left**  
                - Add **hours/day**  
                - Highlight **weak topics**  
                """
            )
            ask_clicked = st.button("✨ Ask ExamGuru AI", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if ask_clicked:
        if not user_input.strip():
            st.info("Please describe your exam details first.")
            return
        if study_sage_executor is None:
            st.error("AI model not configured — set API keys in the **Settings** page.")
            return
        with st.spinner("Thinking like your AI study coach..."):
            result = study_sage_executor.invoke(user_input)

        # Result card
        with st.container():
            st.markdown(
                """
                <div style="padding:1rem 1.2rem; border-radius:0.9rem;
                            background-color:#ECFEFF; border:1px solid #BAE6FD;">
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"### ✅ {result.get('message', 'Plan Created!')}")
            preview = result.get("preview", "")
            if preview:
                st.caption(preview)
            st.markdown("</div>", unsafe_allow_html=True)

        plan = st.session_state.get("last_plan")
        if not plan:
            st.warning("Plan saved in file but could not load into session_state.")
            return
        days = plan.get("plan", [])
        if not days:
            st.info("The plan appears empty.")
            return

        # UI Tabs for better view
        tab1, tab2, tab3 = st.tabs(["📅 Overview", "📋 Table", "🛠 Raw JSON"])

        with tab1:
            # 🔹 Show ALL days and correct count
            total_days = len(days)
            st.subheader(f"Plan Overview ({total_days} Days)")

            for day in days:  # no slicing here → all days
                date_str = day.get("date", "Unknown date")
                tasks = day.get("tasks", [])

                with st.expander(f"{date_str} — {len(tasks)} study blocks", expanded=False):
                    for idx, task in enumerate(tasks, start=1):
                        st.markdown(
                            f"**Block {idx}: {task.get('topic')}**  \n"
                            f"⏱ {task.get('pomodoro_minutes', 0)} min"
                        )
                        if task.get("activity"):
                            st.caption(task["activity"])

        with tab2:
            st.subheader("Compact table (first 15 blocks)")
            rows = []
            # still limiting table to first ~7 days for compactness; adjust if you want
            for day in days[:7]:
                for idx, task in enumerate(day.get("tasks", []), start=1):
                    rows.append({
                        "Date": day.get("date"),
                        "Block": idx,
                        "Topic": task.get("topic"),
                        "Minutes": task.get("pomodoro_minutes"),
                        "Activity": task.get("activity"),
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows))
            else:
                st.info("No tasks found in the current plan.")

        with tab3:
            st.json(plan)
