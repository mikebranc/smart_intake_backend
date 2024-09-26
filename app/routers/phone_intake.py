from fastapi import APIRouter, Request, Response, Query, Depends
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from app.services.intake_service import IntakeService
from app.database import get_db
from app.models import Thread, PhoneMessage
from app.schemas import ThreadCreate, PhoneMessageCreate
import logging
from sqlalchemy.orm import Session
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

router = APIRouter()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/answer")
async def answer(request: Request, thread_id: Optional[int] = Query(default=None)):
    voice_response = VoiceResponse()
    
    if thread_id is None:
        voice_response.say("Hello, I am an AI assistant helping you fill out your intake form. How are you today?")
    
    gather = Gather(
        input="speech",
        speech_timeout="auto",
        speech_model="experimental_conversations",
        enhanced=True,
        action=f"/phone/handle-input?thread_id={thread_id}" if thread_id else "/phone/handle-input"
    )
    voice_response.append(gather)

    return Response(
        content=str(voice_response),
        media_type="application/xml"
    )

@router.post("/handle-input")
async def handle_input(
    request: Request,
    thread_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    voice_input = str(form_data.get("SpeechResult", "No speech input received"))

    # Debug: Log the received input
    print(f"Received speech input: {voice_input}")

    # Create a new thread if it doesn't exist
    if thread_id is None:
        new_thread = Thread(**ThreadCreate().dict())
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        thread_id = new_thread.id

    # Process the voice input using IntakeService
    assistant_response = await IntakeService.process_message(voice_input)

    # Save the message to the database
    new_message = PhoneMessage(**PhoneMessageCreate(
        thread_id=thread_id,
        voice_input=voice_input,
        assistant_response=assistant_response
    ).dict())
    db.add(new_message)
    db.commit()

    voice_response = VoiceResponse()
    voice_response.say(assistant_response)

    # # Check if the conversation is complete
    # if IntakeService.is_conversation_complete(assistant_response):
    #     thread = db.query(Thread).filter(Thread.id == thread_id).first()
    #     thread.completed = True
    #     db.commit()
    #     voice_response.say("Thank you for your time. Goodbye!")
    #     voice_response.hangup()
    # else:
    #     # Redirect back to the answer endpoint with the thread_id
    voice_response.redirect(url=f"/phone/answer?thread_id={thread_id}", method="POST")

    return Response(
        content=str(voice_response),
        media_type="application/xml"
    )

# The last_recording_url function is no longer needed and can be removed
