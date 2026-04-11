from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bot import answer_common_query, generate_weekly_summaries, get_sample_data

app = FastAPI(title="AI Parent Communication Bot")


class ParentQuery(BaseModel):
    parent_name: str
    student_id: str
    message: str


@app.get("/status")
def status():
    return {"status": "running", "service": "AI Parent Communication Bot"}


@app.post("/send-summaries")
def send_summaries():
    payload = generate_weekly_summaries()
    if not payload:
        raise HTTPException(status_code=500, detail="No parent messages were sent.")
    return {"sent": len(payload), "details": payload}


@app.post("/query")
def query(query: ParentQuery):
    answer = answer_common_query(query.message)
    return {
        "parent": query.parent_name,
        "student_id": query.student_id,
        "question": query.message,
        "answer": answer,
    }


@app.get("/sample-data")
def sample_data():
    return get_sample_data()
