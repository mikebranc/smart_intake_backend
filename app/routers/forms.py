from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/templates", response_model=schemas.FormTemplate)
def create_form_template(form_template: schemas.FormTemplateCreate, db: Session = Depends(get_db)):
    db_template = models.FormTemplate(**form_template.dict(exclude={"fields"}))
    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    for field in form_template.fields:
        db_field = models.FormField(**field.dict(), template_id=db_template.id)
        db.add(db_field)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates", response_model=List[schemas.FormTemplate])
def get_form_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.FormTemplate).offset(skip).limit(limit).all()

@router.get("/templates/{template_id}", response_model=schemas.FormTemplate)
def get_form_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Form template not found")
    return db_template

@router.post("/responses", response_model=schemas.FormResponse)
def create_form_response(response: schemas.FormResponseCreate, db: Session = Depends(get_db)):
    db_response = models.FormResponse(template_id=response.template_id)
    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    for field_value in response.field_values:
        db_field_value = models.FormFieldValue(**field_value.dict(), response_id=db_response.id)
        db.add(db_field_value)
    
    db.commit()
    db.refresh(db_response)
    return db_response

@router.get("/responses", response_model=List[schemas.FormResponse])
def get_form_responses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.FormResponse).offset(skip).limit(limit).all()

@router.get("/responses/{response_id}", response_model=schemas.FormResponse)
def get_form_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db.query(models.FormResponse).filter(models.FormResponse.id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Form response not found")
    return db_response