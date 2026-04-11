from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from twilio.twiml.messaging_response import MessagingResponse

from bot import (
    answer_common_query,
    generate_weekly_summaries,
    get_sample_data,
    process_incoming_whatsapp_message,
    validate_twilio_request,
    config,
)

app = FastAPI(title="AI Parent Communication Bot")
scheduler = BackgroundScheduler()


class ParentQuery(BaseModel):
    parent_name: str
    student_id: str
    message: str


@app.on_event("startup")
def start_scheduler():
    cron_expression = config["schedule"]["weekly_summary_cron"]
    scheduler.add_job(
        generate_weekly_summaries,
        CronTrigger.from_crontab(cron_expression),
        id="weekly_summary_job",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)


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


@app.post("/incoming")
async def incoming_whatsapp(request: Request):
    form = await request.form()
    sender = form.get("From")
    body = form.get("Body", "")
    signature = request.headers.get("X-Twilio-Signature", "")

    if not validate_twilio_request(str(request.url), dict(form), signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    answer = process_incoming_whatsapp_message(sender, body)
    response = MessagingResponse()
    response.message(answer)
    return Response(str(response), media_type="application/xml")


@app.get("/sample-data")
def sample_data():
    return get_sample_data()
