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


def get_parent_contact(student_id: str) -> ParentContact | None:
    return next((parent for parent in SAMPLE_PARENTS if parent.student_id == student_id), None)


def get_parent_contact_by_whatsapp(whatsapp_number: str) -> ParentContact | None:
    if not whatsapp_number:
        return None
    normalized = whatsapp_number.strip()
    return next((parent for parent in SAMPLE_PARENTS if parent.whatsapp_number == normalized), None)


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
    text = message.lower()
    if "attendance" in text:
        return "Your child has excellent attendance this week. Please check the next summary for details."
    if "homework" in text or "assignment" in text:
        return "Homework completion is strong. We will send a full breakdown in the weekly report."
    if "grade" in text or "marks" in text:
        return "Grades are updated weekly. The latest summary includes all subjects and performance notes."
    if "improve" in text or "better" in text:
        return "We recommend consistent 15-minute daily practice and reviewing teacher feedback from class."
    if "fee" in text or "payment" in text:
        return "Fee and payment information is shared by school administration. Please contact the school office for the latest invoice details."
    if "hello" in text or "hi" in text or "hey" in text:
        return "Hello! I’m your school support assistant. Ask me about attendance, homework, grades, or request the latest summary."
    return (
        "Thank you for your question. The weekly WhatsApp summary includes grades, attendance, homework status, "
        "behavior notes, and next steps. If you need more detail, ask for the latest summary or contact school staff."
    )


def process_incoming_whatsapp_message(from_number: str, body: str) -> str:
    parent = get_parent_contact_by_whatsapp(from_number)
    if parent is None:
        return (
            "Thanks for contacting the school support bot. We could not find a registered parent account for this WhatsApp number. "
            "Please confirm your registered phone number with the school."
        )

    normalized_body = (body or "").strip().lower()
    if any(keyword in normalized_body for keyword in ["summary", "report", "latest summary", "weekly report"]):
        performance = next((item for item in SAMPLE_PERFORMANCES if item.student_id == parent.student_id), None)
        if performance:
            return generate_summary(performance)
        return "I could not find the latest report for your child. Please contact the school if this persists."

    return answer_common_query(body)


def get_sample_data() -> Dict[str, List[Dict[str, str]]]:
    return {
        "students": [performance.model_dump() for performance in SAMPLE_PERFORMANCES],
        "parents": [parent.model_dump() for parent in SAMPLE_PARENTS],
        "generated_on": str(date.today()),
    }
