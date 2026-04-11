from datetime import date
from typing import Dict, List

from pydantic import BaseModel


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
    ParentContact(parent_name="Mrs. Sharma", whatsapp_number="whatsapp:+919876543210", student_id="STU001"),
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
    # TODO: integrate with WhatsApp API provider (Twilio, Meta, etc.)
    print(f"Sending WhatsApp message to {to_number}:\n{message}\n")


def get_parent_contact(student_id: str) -> ParentContact | None:
    return next((parent for parent in SAMPLE_PARENTS if parent.student_id == student_id), None)


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
    return (
        "Thank you for your question. The weekly WhatsApp summary includes grades, attendance, homework status, "
        "behavior notes, and next steps. If you need more detail, ask for the latest summary or contact school staff."
    )


def get_sample_data() -> Dict[str, List[Dict[str, str]]]:
    return {
        "students": [performance.model_dump() for performance in SAMPLE_PERFORMANCES],
        "parents": [parent.model_dump() for parent in SAMPLE_PARENTS],
        "generated_on": str(date.today()),
    }
