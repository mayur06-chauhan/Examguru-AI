# ExamGuru AI 🎓

ExamGuru AI is an AI-powered exam coach built with **Streamlit**.  
It helps students plan their study schedule, generate flashcards, track progress, and visualize their preparation — all in one place.

---

## 🚀 Features

- **🤖 AI Coach Chat**
  - Describe your exam (subject, days left, hours per day, weak topics).
  - Automatically generates a structured multi-day study plan.
  - Optionally expands syllabus topics using Tavily web search + Gemini.

- **🗓 Planner**
  - Paste your syllabus (one topic per line) or upload a `.txt` file.
  - Configure start/end dates, daily hours, and Pomodoro length.
  - Generates and saves a balanced day-wise study plan.

- **🧠 Flashcards**
  - Generate active-recall flashcards for any topic using Gemini.
  - View flashcards inside the app and download them as JSON.
  - Automatically saves generated flashcards into a `flashcards/` folder.

- **✅ Progress Tracking**
  - Mark which planned tasks you finished on a given date.
  - Self-assess your understanding of a topic (1–5 scale).
  - If your score is low, the plan automatically adapts by adding extra review blocks.

- **📊 Dashboard**
  - Visualizes:
    - Tasks completed over time.
    - Average self-assessment score per topic.
  - Shows overall completion percentage.

- **⚙️ Settings**
  - Select the AI model (currently only **Gemini** is supported).
  - Shows API key status for Gemini.
  - Shows locations of plan, progress, and flashcards storage files.

---

## 🧱 Tech Stack

- **Frontend / App Framework:** Streamlit  
- **AI / LLM Integration:** LangChain + Gemini via `langchain-google-genai`  
- **Web Search (optional):** Tavily via `langchain-community`  
- **Data Handling:** pandas, JSON  
- **Charts:** matplotlib  
- **Config & Secrets:** python-dotenv + `.env`

All Python dependencies are listed in `requirements.txt`.

---

## 📁 Project Structure

A typical layout for this project:

```bash
.
├── app.py
├── tools_agent.py
├── llm_utils.py
├── storage_utils.py
├── study_plan_utils.py
├── config.toml          # Streamlit theme and UI config
├── ui_pages/
│   ├── ai_coach_chat_page.py
│   ├── planner_page.py
│   ├── flashcards_page.py
│   ├── progress_page.py
│   ├── dashboard_page.py
│   └── settings_page.py
├── flashcards/          # Auto-created folder for saving flashcards JSON
├── study_plan_storage.json   # Auto-created plan file
└── study_progress.json       # Auto-created progress file
