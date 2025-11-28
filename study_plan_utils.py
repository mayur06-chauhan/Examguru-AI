# study_plan_utils.py
from datetime import datetime, timedelta
from typing import List, Dict
import json

def parse_syllabus_simple(raw: str) -> List[Dict]:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    topics = []
    for i, l in enumerate(lines):
        topic = l
        weight = round(max(0.6 - i * 0.05, 0.05), 2)
        topics.append({"topic": topic, "weight": weight})
    return topics

def build_study_plan(
    topics: List[Dict],
    start_date: str,
    end_date: str,
    daily_hours: float,
    pomodoro_minutes: int = 25,
) -> Dict:
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    total_days = (end - start).days + 1
    total_minutes = total_days * daily_hours * 60
    total_weight = sum(t.get("weight", 1) for t in topics) or 1

    topic_minutes = []
    for t in topics:
        mins = round(total_minutes * (t.get("weight", 1) / total_weight))
        topic_minutes.append({"topic": t["topic"], "minutes": mins})

    chunk = pomodoro_minutes
    chunks_per_day = max(1, int((daily_hours * 60) // (chunk + 5)))

        # ---- Distribute topics across blocks in a round-robin way ----
    needed_blocks = total_days * chunks_per_day

    # how many blocks per topic, roughly proportional to minutes
    topic_blocks = []
    for tm in topic_minutes:
        blocks = max(1, tm["minutes"] // chunk)
        topic_blocks.append({"topic": tm["topic"], "remaining": blocks})

    # ensure we have at least as many blocks as needed
    def total_remaining():
        return sum(tb["remaining"] for tb in topic_blocks)

    while total_remaining() < needed_blocks:
        for tb in topic_blocks:
            tb["remaining"] += 1
            if total_remaining() >= needed_blocks:
                break

    # round-robin: interleave topics instead of grouping same topic together
    topic_iter: List[str] = []
    while len(topic_iter) < needed_blocks and total_remaining() > 0:
        for tb in topic_blocks:
            if tb["remaining"] > 0:
                topic_iter.append(tb["topic"])
                tb["remaining"] -= 1
                if len(topic_iter) >= needed_blocks:
                    break

    plan = []
    idx = 0
    current = start
    for _ in range(total_days):
        day_tasks = []
        for _ in range(chunks_per_day):
            topic = topic_iter[idx % len(topic_iter)]
            idx += 1
            task = {
                "pomodoro_minutes": chunk,
                "topic": topic,
                "activity": f"Focused study on {topic} — active reading + worked examples",
                "break_minutes": 5,
            }
            day_tasks.append(task)
        day_plan = {
            "date": current.date().isoformat(),
            "tasks": day_tasks,
            "review": "Spend 15 min reviewing previously studied topics (flashcards / quick recall)",
        }
        plan.append(day_plan)
        current += timedelta(days=1)
    return {"plan": plan, "meta": {"created_at": datetime.utcnow().isoformat()}}

def adapt_plan_basic(plan: Dict, topic: str, score: int) -> Dict:
    new_plan = json.loads(json.dumps(plan))  # deep copy
    if score < 3:
        for day in new_plan["plan"]:
            review_task = {
                "pomodoro_minutes": 15,
                "topic": topic,
                "activity": f"Extra review: {topic}",
                "break_minutes": 5,
            }
            day["tasks"].insert(0, review_task)
    return new_plan