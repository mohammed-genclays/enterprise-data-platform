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
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_NUMBER=whatsapp:+your_twilio_whatsapp_number
   TWILIO_WEBHOOK_URL=https://your-domain.com/incoming
   TWILIO_VALIDATE_REQUESTS=false
   ```
4. Update `config.yaml` if you want to change the weekly summary cron schedule.
5. In the Twilio sandbox or WhatsApp sender setup, configure the incoming webhook URL to:
   ```text
   https://your-domain.com/incoming
   ```
   Replace `https://your-domain.com` with your actual public app URL.

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
4. Expose the app for Twilio webhook testing (optional):
   - Use a tunnel like ngrok:
     ```bash
     ngrok http 8000
     ```
   - Point Twilio webhook to `https://<ngrok-id>.ngrok-free.app/incoming`
5. Send summaries manually:
   ```bash
   curl -X POST http://localhost:8000/send-summaries
   ```

## Real-time 24/7 support
- Incoming WhatsApp messages are handled at `/incoming`.
- The bot replies automatically with answers to attendance, homework, grades, improvement tips, and summary requests.
- Automatic weekly summaries are scheduled using the cron expression in `config.yaml`.

## Notes
- For production, keep credentials in environment variables and never commit `.env`.
- The bot still uses sample student data; the next step is to connect your real student/parent datastore.
- Use `TWILIO_VALIDATE_REQUESTS=true` in production after you deploy to a secure public URL.
