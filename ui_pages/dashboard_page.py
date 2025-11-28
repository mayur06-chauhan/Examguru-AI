import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def render_dashboard_page(plan_store, progress_store):
    st.markdown("## 📊 Dashboard")
    st.caption("Visual overview of your study progress and self-assessment trends.")

    total_days = len(plan_store.get("plan", []))
    total_tasks = sum(len(d["tasks"]) for d in plan_store.get("plan", []))
    total_completed = sum(len(e.get("completed_tasks", [])) for e in progress_store.get("entries", []))

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Plan Days", total_days)
    col2.metric("📘 Total Tasks", total_tasks)
    col3.metric("✔ Tasks Completed", total_completed)

    if total_tasks > 0:
        pct = min(100, int((total_completed / total_tasks) * 100))
        st.progress(pct)
        st.caption(f"Overall Completion: **{pct}%**")
    else:
        st.info("No plan yet. Create a plan in the **Planner** page to see analytics.")
        return
    st.markdown("---")

    # Get progress entries
    entries = progress_store.get("entries", [])
    if not entries:
        st.info("No progress recorded yet. Submit progress on the **Progress** page.")
        return

    # ================= Completed Tasks Graph =================
    dfc = pd.DataFrame({
        "date": pd.to_datetime([e["date"] for e in entries]),
        "completed": [len(e["completed_tasks"]) for e in entries],
    }).sort_values("date")
    st.subheader("📈 Completed Tasks Over Time")

    colA, colB = st.columns([1, 3])
    with colB:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(dfc["date"], dfc["completed"], marker="o")
        ax.set_xlabel("Date")
        ax.set_ylabel("Tasks Completed")
        fig.autofmt_xdate()
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

    # ================= Self-Assessment Graph =================
    rows = []
    for e in entries:
        sa = e.get("self_assessment")
        if sa:
            rows.append({"topic": sa["topic"], "score": sa["score"]})

    if rows:
        dfsa = pd.DataFrame(rows)
        grouped = dfsa.groupby("topic")["score"].mean().sort_values(ascending=False)

        st.subheader("🎯 Self-Assessment by Topic")
        colC, colD = st.columns([1, 3])
        with colD:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.bar(grouped.index, grouped.values)
            ax2.set_xticks(range(len(grouped.index)))
            ax2.set_xticklabels(grouped.index, rotation=45, ha="right")
            ax2.set_ylabel("Avg Score")
            plt.tight_layout()
            st.pyplot(fig2)
    else:
        st.info("No self-assessment scores yet. Add them from the **Progress** page.")