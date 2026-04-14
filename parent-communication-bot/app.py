from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

from bot import (
    validate_twilio_request,
    process_incoming_whatsapp_message,
)

app = FastAPI(title="AI Parent Communication Bot")


@app.get("/status")
def status():
    return {"status": "running", "service": "AI Parent Communication Bot"}


@app.post("/incoming")
async def incoming_whatsapp(request: Request):
    form = await request.form()
    sender = form.get("From")
    body = form.get("Body", "")
    signature = request.headers.get("X-Twilio-Signature", "")

    print("📩 From:", sender)
    print("📨 Body:", body)

    validate_twilio_request(str(request.url), dict(form), signature)

    reply = process_incoming_whatsapp_message(sender, body)

    response = MessagingResponse()
    response.message(reply)
    return Response(str(response), media_type="application/xml")
