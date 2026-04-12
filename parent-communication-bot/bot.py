from datetime import date
from typing import Dict, List
import yaml
import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.request_validator import RequestValidator

from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Override with environment variables for security
config['whatsapp']['account_sid'] = os.getenv('TWILIO_ACCOUNT_SID', config['whatsapp']['account_sid'])
config['whatsapp']['auth_token'] = os.getenv('TWILIO_AUTH_TOKEN', config['whatsapp']['auth_token'])
config['whatsapp']['from_number'] = os.getenv('TWILIO_FROM_NUMBER', config['whatsapp']['from_number'])
config['whatsapp']['validate_requests'] = os.getenv(
    'TWILIO_VALIDATE_REQUESTS',
    str(config['whatsapp'].get('validate_requests', False))
).lower() in {'1', 'true', 'yes'}

# Initialize Twilio client
twilio_client = Client(config['whatsapp']['account_sid'], config['whatsapp']['auth_token'])
request_validator = RequestValidator(config['whatsapp']['auth_token'])


class StudentPerformance(BaseModel):
    student_id: str
    student_name: str
    grade: str
    attendance: float
    homework_completion: float
    behavior: str
    highlights: List[str]


class ParentContact(BaseModel):
    parent_name: str
    whatsapp_number: str
    student_id: str


SAMPLE_PERFORMANCES = [
    StudentPerformance(
        student_id="STU001",
        student_name="Aanya Sharma",
        grade="A-",
        attendance=98.0,
        homework_completion=92.0,
        behavior="Excellent participation in class",
        highlights=[
            "Math quiz score: 93%",
            "Science project completed on time",
            "Asked insightful questions in English class",
        ],
    ),
    StudentPerformance(
        student_id="STU002",
        student_name="Imran Khan",
        grade="B+",
        attendance=95.0,
        homework_completion=88.0,
        behavior="Shows consistent effort",
        highlights=[
            "Improved reading fluency",
            "Strong teamwork during the social studies activity",
        ],
    ),
]

SAMPLE_PARENTS = [
    ParentContact(parent_name="Mrs. Sharma", whatsapp_number="whatsapp:+917200374549", student_id="STU001"),
    ParentContact(parent_name="Mr. Khan", whatsapp_number="whatsapp:+919123456789", student_id="STU002"),
]


def generate_summary(performance: StudentPerformance) -> str:
    return (
        f"Weekly Performance Summary for {performance.student_name} ({performance.student_id}):\n"
        f"Grade: {performance.grade}\n"
        f"Attendance: {performance.attendance}%\n"
        f"Homework completion: {performance.homework_completion}%\n"
        f"Behavior: {performance.behavior}\n"
        "Highlights:\n"
        + "\n".join(f"- {item}" for item in performance.highlights)
    )


def send_whatsapp_message(to_number: str, message: str) -> None:
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=config['whatsapp']['from_number'],
            to=to_number,
        )
        print(f"WhatsApp message sent successfully. SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp message to {to_number}: {str(e)}")


def validate_twilio_request(url: str, params: Dict[str, str], signature: str) -> bool:
    if not config['whatsapp']['validate_requests']:
        return True
    if not signature:
        return False
    return request_validator.validate(url, params, signature)


def normalize_whatsapp_number(number: str) -> str:
    if not number:
        return ""
    normalized = number.strip().lower()
    if normalized.startswith("whatsapp:"):
        normalized = normalized[len("whatsapp:") :]
    return normalized.replace(" ", "").replace("-", "")


def get_parent_contact(student_id: str) -> ParentContact | None:
    return next((parent for parent in SAMPLE_PARENTS if parent.student_id == student_id), None)


def get_parent_contact_by_whatsapp(whatsapp_number: str) -> ParentContact | None:
    normalized = normalize_whatsapp_number(whatsapp_number)
    if not normalized:
        return None
    return next(
        (
            parent
            for parent in SAMPLE_PARENTS
            if normalize_whatsapp_number(parent.whatsapp_number) == normalized
        ),
        None,
    )


def log_parent_query(parent: ParentContact | None, incoming: str, response: str) -> None:
    parent_info = parent.student_id if parent else "unknown"
    print(
        f"[ParentQuery] parent={parent_info} incoming={incoming!r} response={response!r}"
    )


def generate_weekly_summaries() -> List[Dict[str, str]]:
    payload = []
    for performance in SAMPLE_PERFORMANCES:
        contact = get_parent_contact(performance.student_id)
        if contact is None:
            continue
        summary = generate_summary(performance)
        send_whatsapp_message(contact.whatsapp_number, summary)
        payload.append({"parent": contact.parent_name, "student": performance.student_name, "status": "sent"})
    return payload


def answer_common_query(message: str) -> str:
    text = (message or "").lower()
    if "attendance" in text:
        return "Your child has excellent attendance this week. The latest summary includes full attendance details."
    if "homework" in text or "assignment" in text:
        return "Homework completion is strong. I will share the full breakdown in the next weekly report."
    if "grade" in text or "marks" in text:
        return "Grades are updated weekly. Review the latest summary for all subject notes and guidance."
    if "improve" in text or "better" in text:
        return "I recommend 15 minutes of daily review and checking teacher feedback in the latest summary."
    if "behavior" in text or "conduct" in text or "discipline" in text:
        return "Behavior and participation notes are included in the weekly report. Your child is making steady progress."
    if "exam" in text or "test" in text or "schedule" in text:
        return "Exam and test schedules are shared by the school. I can provide the latest performance summary once it is available."
    if "fee" in text or "payment" in text:
        return "Fee payment status is maintained by the school office. I can only share academic and attendance updates right now."
    if "hello" in text or "hi" in text or "hey" in text or "good morning" in text:
        return "Hello! I’m your school support bot. Ask me about attendance, homework, grades, behavior, or request the latest summary."
    if "summary" in text or "report" in text or "latest report" in text:
        return "Please ask for the latest summary by sending 'latest summary' or 'report' and I will share your child's most recent update."

    return (
        "I’m available 24/7 to support you. You can ask about attendance, homework, grades, behavior, or request the latest summary. "
        "If you need a specific report, send a message like 'latest summary' or 'homework update'."
    )


def process_incoming_whatsapp_message(from_number: str, body: str) -> str:
    parent = get_parent_contact_by_whatsapp(from_number)
    normalized_body = (body or "").strip()

    if parent is None:
        response = (
            "Thanks for contacting the school support bot. I could not find your registered parent profile. "
            "Please confirm the number registered with the school and try again."
        )
        log_parent_query(None, normalized_body, response)
        return response

    lower_body = normalized_body.lower()
    if any(keyword in lower_body for keyword in ["summary", "report", "latest summary", "weekly report"]):
        performance = next((item for item in SAMPLE_PERFORMANCES if item.student_id == parent.student_id), None)
        if performance:
            response = generate_summary(performance)
            log_parent_query(parent, normalized_body, response)
            return response
        response = "I could not find the latest report for your child right now. Please try again later."
        log_parent_query(parent, normalized_body, response)
        return response

    response = answer_common_query(normalized_body)
    log_parent_query(parent, normalized_body, response)
    return response


def get_sample_data() -> Dict[str, List[Dict[str, str]]]:
    return {
        "students": [performance.model_dump() for performance in SAMPLE_PERFORMANCES],
        "parents": [parent.model_dump() for parent in SAMPLE_PARENTS],
        "generated_on": str(date.today()),
    }
