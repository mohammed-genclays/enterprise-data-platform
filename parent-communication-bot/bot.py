
# -----------------------
# In‑memory session store
# -----------------------
parent_sessions = {}

from datetime import date
from typing import Dict, List
import os
import yaml
from dotenv import load_dotenv

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from pydantic import BaseModel
from google.cloud import bigquery

# ------------------------------------------------------------------
# Load config
# ------------------------------------------------------------------

load_dotenv()

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

config["whatsapp"]["account_sid"] = os.getenv(
    "TWILIO_ACCOUNT_SID", config["whatsapp"]["account_sid"]
)
config["whatsapp"]["auth_token"] = os.getenv(
    "TWILIO_AUTH_TOKEN", config["whatsapp"]["auth_token"]
)
config["whatsapp"]["from_number"] = os.getenv(
    "TWILIO_FROM_NUMBER", config["whatsapp"]["from_number"]
)
config["whatsapp"]["validate_requests"] = os.getenv(
    "TWILIO_VALIDATE_REQUESTS",
    str(config["whatsapp"].get("validate_requests", False)),
).lower() in {"1", "true", "yes"}

# ------------------------------------------------------------------
# Twilio
# ------------------------------------------------------------------

twilio_client = Client(
    config["whatsapp"]["account_sid"], config["whatsapp"]["auth_token"]
)
request_validator = RequestValidator(config["whatsapp"]["auth_token"])

# ------------------------------------------------------------------
# BigQuery
# ------------------------------------------------------------------

bq_client = bigquery.Client(project=config["bigquery"]["project_id"])
BQ_DATASET = f'{config["bigquery"]["project_id"]}.{config["bigquery"]["dataset"]}'

# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------

class ParentContact(BaseModel):
    parent_id: str
    parent_name: str
    whatsapp_number: str
    student_id: str
    student_name: str
    grade: str
    section: str

# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------

def validate_twilio_request(url: str, params: Dict[str, str], signature: str) -> bool:
    if not config["whatsapp"]["validate_requests"]:
        return True
    if not signature:
        return False
    return request_validator.validate(url, params, signature)


def normalize_whatsapp_number(number: str) -> str:
    if not number:
        return ""
    normalized = number.lower().strip()
    if normalized.startswith("whatsapp:"):
        normalized = normalized[len("whatsapp:") :]
    return normalized.replace(" ", "").replace("-", "")

# ------------------------------------------------------------------
# Parent & children resolution (MULTI‑CHILD)
# ------------------------------------------------------------------

def get_children_for_parent(whatsapp_number: str) -> List[ParentContact]:
    normalized = normalize_whatsapp_number(whatsapp_number)

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
    JOIN `{BQ_DATASET}.student_parent_map` spm
      ON p.parent_id = spm.parent_id
    JOIN `{BQ_DATASET}.students` s
      ON spm.student_id = s.student_id
    WHERE p.phone_number = @phone
      AND p.is_active = TRUE
      AND s.is_active = TRUE
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("phone", "STRING", normalized)
        ]
    )

    rows = list(bq_client.query(query, job_config=job_config))
    return [ParentContact(**row) for row in rows]


def prompt_child_selection(children: List[ParentContact]) -> str:
    lines = ["You have multiple children registered:\n"]
    for i, c in enumerate(children, start=1):
        lines.append(f"{i}️⃣ {c.student_name} ({c.grade}-{c.section})")
    lines.append("\nReply with the number to continue.")
    return "\n".join(lines)

# ------------------------------------------------------------------
# Attendance
# ------------------------------------------------------------------

def get_weekly_attendance(student_id: str) -> float:
    query = f"""
    SELECT
      COUNTIF(status = 'Present') * 100.0 / COUNT(*) AS attendance_pct
    FROM `{BQ_DATASET}.attendance_daily`
    WHERE student_id = @student_id
      AND attendance_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("student_id", "STRING", student_id)
        ]
    )

    rows = list(bq_client.query(query, job_config=job_config))
    pct = rows[0].attendance_pct if rows else None
    return round(pct, 2) if pct is not None else 0.0


def generate_attendance_summary(parent: ParentContact) -> str:
    attendance = get_weekly_attendance(parent.student_id)
    return (
        "📊 Weekly Attendance Summary\n\n"
        f"Student: {parent.student_name}\n"
        f"Class: {parent.grade}-{parent.section}\n"
        f"Attendance: {attendance}%\n\n"
        "Thank you for supporting your child’s learning."
    )

# ------------------------------------------------------------------
# Homework
# ------------------------------------------------------------------

def get_today_homework(student_id: str) -> str:
    query = f"""
    SELECT subject, status
    FROM `{BQ_DATASET}.homework_daily`
    WHERE student_id = @student_id
      AND homework_date = CURRENT_DATE()
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("student_id", "STRING", student_id)
        ]
    )

    rows = list(bq_client.query(query, job_config=job_config))
    if not rows:
        return "📘 No homework assigned for today."

    lines = ["📘 Today's Homework:"]
    for r in rows:
        lines.append(f"- {r.subject}: {r.status}")
    return "\n".join(lines)

# ------------------------------------------------------------------
# Grades
# ------------------------------------------------------------------

def get_recent_grades(student_id: str) -> str:
    query = f"""
    SELECT subject, score, max_score
    FROM `{BQ_DATASET}.grades_summary`
    WHERE student_id = @student_id
    ORDER BY graded_on DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("student_id", "STRING", student_id)
        ]
    )

    rows = list(bq_client.query(query, job_config=job_config))
    if not rows:
        return "📊 No grades available yet."

    lines = ["📊 Recent Grades:"]
    for r in rows:
        lines.append(f"- {r.subject}: {r.score}/{r.max_score}")
    return "\n".join(lines)

# ------------------------------------------------------------------
# MAIN BOT LOGIC (ALL FEATURES)
# ------------------------------------------------------------------

def process_incoming_whatsapp_message(from_number: str, body: str) -> str:
    incoming = (body or "").strip().lower()

    # ✅ 1. Handle greetings FIRST (always respond)
    if incoming in {"hi", "hello", "hey", "good morning", "good evening"}:
        return (
            "Hello! 👋 I can help you with:\n\n"
            "• Attendance\n"
            "• Homework\n"
            "• Grades\n"
            "• Weekly Summary\n\n"
            "You can also type 'switch child' to change the selected student."
        )

    # ✅ 2. Resolve children
    children = get_children_for_parent(from_number)
    if not children:
        return (
            "We could not find your registration details. "
            "Please contact the school office."
        )

    session = parent_sessions.get(from_number)

    # ✅ 3. Handle child selection if multiple children
    if incoming.isdigit() and len(children) > 1:
        idx = int(incoming) - 1
        if 0 <= idx < len(children):
            parent_sessions[from_number] = children[idx]
            selected = children[idx]
            return (
                f"✅ Selected child: {selected.student_name} "
                f"({selected.grade}-{selected.section})\n\n"
                "How can I help you?\n"
                "• Attendance\n"
                "• Homework\n"
                "• Grades\n"
                "• Weekly Summary"
            )
        else:
            return "❌ Invalid selection. Please reply with a valid number."

    # ✅ 4. Ask for child selection if needed
    if len(children) > 1 and session is None:
        return prompt_child_selection(children)

    # ✅ 5. Resolve selected child
    selected = session if session else children[0]

    # ✅ 6. Intent routing
    if "attendance" in incoming:
        return generate_attendance_summary(selected)

    if "homework" in incoming:
        return get_today_homework(selected.student_id)

    if "grades" in incoming:
        return get_recent_grades(selected.student_id)

    if "summary" in incoming:
        return (
            generate_attendance_summary(selected)
            + "\n\n"
            + get_today_homework(selected.student_id)
        )

    if "switch" in incoming or "change" in incoming:
        parent_sessions.pop(from_number, None)
        return prompt_child_selection(children)

    # ✅ 7. Final fallback (always respond)
    return (
        "I can help you with:\n\n"
        "• Attendance\n"
        "• Homework\n"
        "• Grades\n"
        "• Weekly Summary\n\n"
        "Type 'switch child' to change the selected student."
    )

# ------------------------------------------------------------------
# Scheduled weekly summaries
# ------------------------------------------------------------------

def generate_weekly_summaries() -> List[Dict[str, str]]:
    payload = []

    query = f"""
    SELECT DISTINCT
      p.phone_number,
      p.parent_name,
      s.student_name,
      s.student_id,
      s.grade,
      s.section
    FROM `{BQ_DATASET}.parents` p
    JOIN `{BQ_DATASET}.student_parent_map` spm
      ON p.parent_id = spm.parent_id
    JOIN `{BQ_DATASET}.students` s
      ON spm.student_id = s.student_id
    WHERE p.is_active = TRUE
      AND s.is_active = TRUE
    """

    for row in bq_client.query(query):
        parent = ParentContact(**row)
        message = generate_attendance_summary(parent)
        twilio_client.messages.create(
            body=message,
            from_=config["whatsapp"]["from_number"],
            to=f"whatsapp:{parent.whatsapp_number}",
        )
        payload.append(
            {
                "parent": parent.parent_name,
                "student": parent.student_name,
                "status": "sent",
            }
        )

    return payload


def answer_common_query(message: str) -> str:
    return (
        "You can ask me about attendance, homework, grades or weekly summary."
    )


def get_sample_data() -> Dict[str, str]:
    return {
        "message": "Sample endpoint disabled. Data is now sourced from BigQuery.",
        "generated_on": str(date.today()),
    }
