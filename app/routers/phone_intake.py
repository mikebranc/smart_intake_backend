from fastapi import APIRouter, Request, Response, Query, Depends
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from app.services.intake_service import process_message
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
async def answer(request: Request, thread_id: Optional[int] = Query(default=None), db: Session = Depends(get_db)):
    voice_response = VoiceResponse()
    
    if thread_id is None:
        # Create a new thread
        new_thread = Thread(**ThreadCreate(completed=False).dict())
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        thread_id = new_thread.id
        greeting = "Hello, I am an AI assistant helping you fill out your intake form. How are you today?"
        
        # Create a PhoneMessage for the initial greeting
        new_message = PhoneMessage(**PhoneMessageCreate(
            thread_id=thread_id,
            voice_input="",  # No human input for the initial greeting
            assistant_response=greeting
        ).dict())
        db.add(new_message)
        db.commit()
        
        # Add the initial greeting
        voice_response.say(greeting)
    
    gather = Gather(
        input="speech",
        speech_timeout="auto",
        speech_model="experimental_conversations",
        enhanced=True,
        action=f"/phone/handle-input?thread_id={thread_id}"
    )
    voice_response.append(gather)

    return Response(
        content=str(voice_response),
        media_type="application/xml"
    )

@router.post("/handle-input")
async def handle_input(
    request: Request,
    thread_id: int = Query(...),  # Now required
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    voice_input = str(form_data.get("SpeechResult", "No speech input received"))

    print(f"Received speech input: {voice_input}")

    # Pass thread_id to process_message
    assistant_response = await process_message(voice_input, db, thread_id=thread_id)

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

    # Redirect back to the answer endpoint with the thread_id
    voice_response.redirect(url=f"/phone/answer?thread_id={thread_id}", method="POST")

    return Response(
        content=str(voice_response),
        media_type="application/xml"
    )

# The last_recording_url function is no longer needed and can be removed
