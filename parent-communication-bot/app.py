from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
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


@app.post("/incoming")
async def incoming_whatsapp(request: Request):
    print(f"[INCOMING REQUEST] method={request.method} url={request.url}")
    try:
        form = await request.form()
        print(f"[FORM PARSED] {dict(form)}")
        sender = form.get("From")
        body = form.get("Body", "")
        signature = request.headers.get("X-Twilio-Signature", "")

        if not validate_twilio_request(str(request.url), dict(form), signature):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

        answer = process_incoming_whatsapp_message(sender, body)
        response = MessagingResponse()
        response.message(answer)
        return Response(str(response), media_type="application/xml")
    except Exception as exc:
        import traceback

        print("[incoming webhook error]", exc)
        print(traceback.format_exc())
        raise


@app.get("/sample-data")
def sample_data():
    return get_sample_data()
