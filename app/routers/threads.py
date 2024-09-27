from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Thread])
def get_threads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Thread).offset(skip).limit(limit).all()

@router.get("/{thread_id}", response_model=schemas.Thread)
def get_thread(thread_id: int, db: Session = Depends(get_db)):
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    print(thread)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread

@router.get("/{thread_id}/messages", response_model=List[schemas.PhoneMessage])
def get_thread_messages(thread_id: int, db: Session = Depends(get_db)):
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread.messages