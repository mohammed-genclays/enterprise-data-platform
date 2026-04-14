# -----------------------
# In-memory session store
# -----------------------
# { from_number: { "student": ParentContact, "last_intent": str } }
parent_sessions = {}

import threading
import os
import yaml
from typing import List, Dict
from dotenv import load_dotenv
from pydantic import BaseModel
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from google.cloud import bigquery

from ai_intent import detect_intent
from ai_summary import (
    ai_generate_summary,
    ai_generate_improvement_plan
)


# -----------------------
# Load config
# -----------------------
load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
request_validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))


def validate_twilio_request(url: str, params: Dict[str, str], signature: str) -> bool:
    if not signature:
        return True
    return request_validator.validate(url, params, signature)


# -----------------------
# BigQuery
# -----------------------
bq_client = bigquery.Client(project=config["bigquery"]["project_id"])
BQ_DATASET = f'{config["bigquery"]["project_id"]}.{config["bigquery"]["dataset"]}'


# -----------------------
# Models
# -----------------------
class ParentContact(BaseModel):
    parent_id: str
    parent_name: str
    whatsapp_number: str
    student_id: str
    student_name: str
    grade: str
    section: str


# -----------------------
# Utilities
# -----------------------
def normalize_whatsapp(number: str) -> str:
    return number if number.startswith("whatsapp:") else f"whatsapp:{number}"


# -----------------------
# Data Access
# -----------------------
def get_children_for_parent(whatsapp: str) -> List[ParentContact]:
    phone = whatsapp.replace("whatsapp:", "")
    query = f"""
    SELECT
        p.parent_id,
        p.parent_name,
        p.phone_number AS whatsapp_number,
        s.student_id,
        s.student_name,
        s.grade,
        s.section
    FROM `{BQ_DATASET}.parents` p
    JOIN `{BQ_DATASET}.student_parent_map` spm ON p.parent_id = spm.parent_id
    JOIN `{BQ_DATASET}.students` s ON spm.student_id = s.student_id
    WHERE p.phone_number = @phone
    """

    job = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("phone", "STRING", phone)]
    )
    rows = list(bq_client.query(query, job_config=job))
    return [ParentContact(**r) for r in rows]


def get_weekly_attendance(student_id: str) -> float:
    query = f"""
    SELECT COUNTIF(status='Present') * 100.0 / COUNT(*) AS pct
    FROM `{BQ_DATASET}.attendance_daily`
    WHERE student_id=@sid
      AND attendance_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    """
    job = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("sid", "STRING", student_id)]
    )
    rows = list(bq_client.query(query, job_config=job))
    return round(rows[0].pct, 2) if rows and rows[0].pct else 0.0


def get_today_homework(student_id: str) -> str:
    query = f"""
    SELECT subject, status
    FROM `{BQ_DATASET}.homework_daily`
    WHERE student_id=@sid AND homework_date=CURRENT_DATE()
    """
    job = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("sid", "STRING", student_id)]
    )
    rows = list(bq_client.query(query, job_config=job))
    if not rows:
        return "📘 No homework assigned today."
    return "\n".join(f"- {r.subject}: {r.status}" for r in rows)


def get_recent_grades(student_id: str) -> str:
    query = f"""
    SELECT subject, score, max_score
    FROM `{BQ_DATASET}.grades_summary`
    WHERE student_id=@sid
    """
    job = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("sid", "STRING", student_id)]
    )
    rows = list(bq_client.query(query, job_config=job))
    if not rows:
        return "📊 No grades available."
    return "\n".join(f"- {r.subject}: {r.score}/{r.max_score}" for r in rows)


# -----------------------
# ASYNC AI HELPERS
# -----------------------
def send_ai_summary_async(from_number: str, student: ParentContact):
    attendance = get_weekly_attendance(student.student_id)
    homework = get_today_homework(student.student_id)
    grades = get_recent_grades(student.student_id)

    ai_text = ai_generate_summary(attendance, homework, grades)
    if not ai_text:
        ai_text = f"Attendance: {attendance}%\n{homework}\n{grades}"

    twilio_client.messages.create(
        from_=config["whatsapp"]["from_number"],
        to=normalize_whatsapp(from_number),
        body=ai_text
    )

def send_ai_improvement_plan_async(from_number: str, student: ParentContact):
    try:
        attendance = get_weekly_attendance(student.student_id)
        homework = get_today_homework(student.student_id)
        grades = get_recent_grades(student.student_id)

        ai_text = ai_generate_improvement_plan(attendance, homework, grades)

        if not ai_text:
            ai_text = (
                "Here are some general improvement suggestions:\n"
                "- Encourage regular attendance\n"
                "- Ensure homework is completed daily\n"
                "- Spend time revising Maths and English\n"
                "- Communicate with the class teacher"
            )

        message_parts = split_message(ai_text)

        for part in message_parts:
            twilio_client.messages.create(
                from_=config["whatsapp"]["from_number"],
                to=normalize_whatsapp(from_number),
                body=part
            )

    except Exception as e:
        print("⚠️ IMPROVEMENT PLAN AI ERROR:", e)

def split_message(text: str, limit: int = 1500) -> list[str]:
    """
    Split long text into chunks safe for WhatsApp/Twilio.
    """
    chunks = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


# -----------------------
# MAIN BOT LOGIC
# -----------------------
def process_incoming_whatsapp_message(from_number: str, body: str) -> str:
    incoming = body.strip().lower()

    children = get_children_for_parent(from_number)
    if not children:
        return "❌ Your number is not registered with the school."

    session = parent_sessions.get(from_number)

    # Child selection
    if incoming.isdigit() and len(children) > 1:
        idx = int(incoming) - 1
        parent_sessions[from_number] = {
            "student": children[idx],
            "last_intent": None
        }
        return f"✅ Selected {children[idx].student_name}. How can I help?"

    if len(children) > 1 and session is None:
        return "\n".join(
            ["You have multiple children:"] +
            [f"{i+1}. {c.student_name} ({c.grade}-{c.section})"
             for i, c in enumerate(children)]
        )

    if isinstance(session, dict):
        selected = session["student"]
        last_intent = session.get("last_intent")
    else:
        selected = children[0]
        last_intent = None

    intent = detect_intent(incoming)["intent"]
    print("AI intent detected:", intent)

    # ✅ FOLLOW-UP CONTEXT
    if last_intent == "summary" and "improve" in incoming:
        intent = "improvement_plan"

    if intent == "summary":
        parent_sessions[from_number]["last_intent"] = "summary"
        threading.Thread(
            target=send_ai_summary_async,
            args=(from_number, selected),
            daemon=True
        ).start()
        return "⏳ Fetching detailed summary for you…"

    if intent == "improvement_plan":
        threading.Thread(
            target=send_ai_improvement_plan_async,
            args=(from_number, selected),
            daemon=True
        ).start()
        return "⏳ Creating an improvement plan…"

    if intent == "attendance":
        return f"📊 Attendance this week: {get_weekly_attendance(selected.student_id)}%"

    if intent == "homework":
        return get_today_homework(selected.student_id)

    if intent == "grades":
        return get_recent_grades(selected.student_id)

    if intent == "greeting":
        return (
            "Hello! 👋 You can ask:\n"
            "- How is my child doing?\n"
            "- Suggest improvement plan\n"
            "- Attendance this week\n"
            "- Homework\n"
            "- Grades"
        )

    return "I can help with attendance, homework, grades, or summaries."