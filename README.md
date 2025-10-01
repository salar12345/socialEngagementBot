# Social Network Engagement Bot

A FastAPI-based service that monitors mock social media profiles, tracks follower counts, stores history in SQLite, and sends Telegram alerts when milestones are reached.

## Setup

1. Create virtualenv and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` → `.env` and set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

3. Run demo setup:
   ```bash
   python run_demo.py
   ```

4. Start the app:
   ```bash
   uvicorn main:app --reload
   ```

API docs available at: http://127.0.0.1:8000/docs
