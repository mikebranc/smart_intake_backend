from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.intake_service import process_message, get_form_data
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

class ChatMessage(BaseModel):
    content: str

class ChatResponse(BaseModel):
    messages: List[Dict[str, str]]

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    response = await process_message(message.content, db)
    return ChatResponse(messages=[{"role": "assistant", "content": response}])

@router.get("/form-data")
async def fetch_form_data(db: Session = Depends(get_db)):
    data = get_form_data(db)
    if not data:
        raise HTTPException(status_code=404, detail="No form data available")
    return data