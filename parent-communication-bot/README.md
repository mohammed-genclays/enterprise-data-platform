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
- `config.yaml`: placeholder configuration for WhatsApp integration and schedule settings
- `requirements.txt`: Python dependencies

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
- Replace the WhatsApp integration placeholder in `bot.py` with a real WhatsApp API provider such as Twilio or Meta Business API.
- Use environment variables to store sensitive credentials.
