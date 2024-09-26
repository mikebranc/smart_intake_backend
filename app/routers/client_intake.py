from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.intake_service import IntakeService
from typing import List, Dict

router = APIRouter()

class ChatMessage(BaseModel):
    content: str

class ChatResponse(BaseModel):
    messages: List[Dict[str, str]]

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    response = await IntakeService.process_message(message.content)
    return ChatResponse(messages=[{"role": "assistant", "content": response}])

@router.get("/form-data")
async def get_form_data():
    data = IntakeService.get_form_data()
    if not data:
        raise HTTPException(status_code=404, detail="No form data available")
    return data