
# 🤖 AI Parent Communication Bot

## 📘 Problem Statement
Parents receive scattered and chaotic updates through WhatsApp groups. Individual student performance insights are missing, and school staff spend a significant amount of time answering repetitive questions such as attendance, homework, and marks.

---

## ✅ Solution
AI Parent Communication Bot is a conversational assistant for schools that:

- Provides **personalized, student‑specific insights** to parents
- Answers parent queries **24×7** via chat
- Generates **AI‑based performance summaries and improvement plans**
- Supports **parents with multiple children**
- Significantly **reduces teacher and admin workload**

The system combines **structured school data** with an **AI explanation layer** (AI never writes or alters school data).

---

## 🧠 Key Features

- ✅ Multi‑child parent support
- ✅ Natural language questions (no commands needed)
- ✅ AI performance summaries
- ✅ AI improvement plans (context‑aware follow‑up questions)
- ✅ Asynchronous messaging (no WhatsApp timeouts)
- ✅ BigQuery as source of truth
- ✅ Local AI using **Ollama + LLaMA‑3** (development & pilot)

---

## 🗂 Project Structure

```
parent-communication-bot/
│
├── app.py                  # FastAPI webhook (Twilio entry point)
├── bot.py                  # Core bot logic + async AI handling
├── ai_service.py           # LLM interface (Ollama for local use)
├── ai_intent.py            # AI intent detection logic
├── ai_summary.py           # AI prompts for summaries & improvement plans
│
├── config.yaml             # WhatsApp + BigQuery configuration
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

---

## 🧩 System Architecture (Local Development)

```
Parent (WhatsApp)
        ↓
      Twilio
        ↓
FastAPI /incoming endpoint
        ↓
Immediate response (≤10 seconds)
        ↓
Async background AI task
        ↓
Ollama (LLaMA‑3)
        ↓
Split response → WhatsApp
```

✅ Designed to avoid Twilio timeouts  
✅ Matches production WhatsApp patterns

---

## 🔧 Prerequisites

- Python **3.10+**
- Git
- Twilio account (WhatsApp Sandbox for development)
- Google Cloud BigQuery access
- Local system with **16 GB RAM minimum** (32 GB recommended for Ollama)

---

## 🧠 Local AI Setup – Ollama

### 1️⃣ Install Ollama

Download from:
https://ollama.com

Verify installation:
```
ollama --version
```

---

### 2️⃣ Pull LLaMA‑3 model

```
ollama pull llama3:8b
```

---

### 3️⃣ Warm up the model (important)

```
ollama run llama3:8b
```
Type:
```
hello
```
Wait for response → press **Ctrl+C**

✅ Prevents slow first response from the bot

---

## 🔐 Environment Variables

Copy example file:
```
cp .env.example .env
```

Update `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=whatsapp:+14155238886
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

⚠️ Never commit `.env` to version control

---

## ⚙️ Configuration

Edit `config.yaml`:

```
whatsapp:
  from_number: "whatsapp:+14155238886"
  validate_requests: false

bigquery:
  project_id: "your-gcp-project"
  dataset: "school_bot_dev"
```

---

## 🚀 Run Locally

### 1️⃣ Create virtual environment

```
python -m venv .venv
source .venv/bin/activate      # Linux / Mac
.\.venv\Scripts\Activate.ps1  # Windows
```

---

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

### 3️⃣ Start the FastAPI app

```
C:\Users\Rafeeq\Documents\git_repo\enterprise-data-platform\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000
```

Test:
```
http://localhost:8000/status
```

---

### 4️⃣ Expose webhook for Twilio testing

```
ngrok http 8000
```

Set Twilio webhook:
```
https://<ngrok-id>.ngrok-free.app/incoming
```

---

## 💬 Bot Usage Examples

```
hi
→ Select child

How is my child doing?
→ AI summary (async)

Suggest improvement plan
→ AI improvement steps (async)

Attendance this week
→ 66.7%

Math marks
→ 38 / 50
```

---

## ⏱ Async Messaging Design

- Webhook responds immediately to Twilio
- AI responses are generated asynchronously
- Long responses are split into multiple WhatsApp messages

✅ No webhook timeouts  
✅ Stable production pattern

---

## ⚠️ Twilio Sandbox Limitations

- Strict daily message limits
- Intended only for testing
- Long AI usage will exceed quota quickly

✅ Use sandbox **only for development**  
✅ Production requires **WhatsApp Business API**

---

## 🧪 Data Assumptions

The bot reads from BigQuery tables:
- `parents`
- `students`
- `student_parent_map`
- `attendance_daily`
- `homework_daily`
- `grades_summary`

Teachers do not interact with the bot directly.

---

## 🔒 Security Notes

- Enable request validation in production
- Always use HTTPS
- AI never modifies student data
- AI output is explainable and supportive

---

## ✅ Current Status

- ✅ Bot logic complete
- ✅ AI summaries and follow-ups working
- ✅ Async WhatsApp pattern stable
- ✅ Ready for real-world deployment

---

## 🚀 Next Steps

- Deploy to GCP VM (always-on)
- Move from Twilio Sandbox → WhatsApp Business API
- Add monitoring and logs
- Pilot with 1–2 classes
