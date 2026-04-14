from ai_service import call_llm

SUMMARY_PROMPT = """
Summarize the student performance in simple, parent-friendly language.
Use only the data below.


Attendance: {attendance}%
Homework:
{homework}

Grades:
{grades}
"""

def ai_generate_summary(attendance, homework, grades):
    prompt = SUMMARY_PROMPT.format(
        attendance=attendance,
        homework=homework,
        grades=grades,
    )

    summary = call_llm(prompt)

    if not summary:
        return None

    return summary

IMPROVEMENT_PROMPT = """
You are an educational assistant.

Based on the student's data below, suggest a simple and practical
improvement plan for parents to follow at home.

Guidelines:
- Be constructive and encouraging
- Give 3–5 clear, actionable steps
- Avoid blame or negative language
- Use bullet points

Student data:
Attendance: {attendance}%
Homework: {homework}
Grades: {grades}
"""

def ai_generate_improvement_plan(attendance, homework, grades):
    prompt = IMPROVEMENT_PROMPT.format(
        attendance=attendance,
        homework=homework,
        grades=grades
    )
    return call_llm(prompt)

from ai_service import call_llm

IMPROVEMENT_PLAN_PROMPT = """
You are an educational assistant.

Based on the student's data below, suggest a simple and practical
IMPROVEMENT PLAN for parents to follow.

Rules:
- Give 4–6 clear, actionable steps
- Be constructive and encouraging
- Avoid repeating performance summary
- Focus on what can be done NEXT
- Use bullet points

Student data:
Attendance: {attendance}%
Homework: {homework}
Grades: {grades}
"""

def ai_generate_improvement_plan(attendance, homework, grades):
    prompt = IMPROVEMENT_PLAN_PROMPT.format(
        attendance=attendance,
        homework=homework,
        grades=grades
    )
    return call_llm(prompt)