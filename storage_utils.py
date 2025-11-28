# storage_utils.py
import os
import json
PLAN_FILE = "study_plan_storage.json"
PROGRESS_FILE = "study_progress.json"
FLASHCARDS_DIR = "flashcards"

os.makedirs(FLASHCARDS_DIR, exist_ok=True)

def load_json_or_default(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)