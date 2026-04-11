# AI Parent Communication Bot

## Problem
Parents receive scattered, chaotic updates through WhatsApp groups. Individual student performance updates are missing and staff spend too much time responding to routine questions.

## Solution
AI Parent Communication Bot automatically:
- sends personalized weekly performance summaries to each parent via WhatsApp
- answers common parent queries 24/7
- reduces manual staff effort and improves parent engagement

## Project Structure
- `app.py`: FastAPI service with endpoints for sending summaries and receiving parent queries
- `bot.py`: summary generation, communication helpers, and simple AI query handling
- `config.yaml`: configuration for WhatsApp integration and schedule settings
- `.env.example`: example environment variables for secure credential storage
- `requirements.txt`: Python dependencies

## Setup WhatsApp Integration (Twilio)
1. Sign up for a [Twilio account](https://www.twilio.com/).
2. Enable WhatsApp in your Twilio console and get a WhatsApp-enabled phone number.
3. Copy `.env.example` to `.env` and fill in your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_NUMBER=whatsapp:+your_twilio_whatsapp_number
   ```
4. Update `config.yaml` with your settings (or rely on env vars).

## Run locally
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
4. Send summaries manually:
   ```bash
   curl -X POST http://localhost:8000/send-summaries
   ```

## Notes
- For production, use environment variables for all secrets.
- The bot currently uses sample data; integrate with real student/parent databases next.
- Schedule automated summaries using the cron expression in `config.yaml`.
