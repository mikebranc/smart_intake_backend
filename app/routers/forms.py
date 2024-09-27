from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/templates", response_model=schemas.FormTemplate)
def create_form_template(form_template: schemas.FormTemplateCreate, db: Session = Depends(get_db)):
    db_template = models.FormTemplate(**form_template.dict(exclude={"fields"}))
    db.add(db_template)
    db.flush()

    for field in form_template.fields:
        db_field = models.FormField(
            **field.dict(exclude={"id", "field_type"}),
            field_type=models.FieldType[field.field_type.upper()],
            template_id=db_template.id
        )
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

@router.put("/templates/{template_id}", response_model=schemas.FormTemplate)
def update_form_template(template_id: int, form_template: schemas.FormTemplateUpdate, db: Session = Depends(get_db)):
    db_template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Form template not found")

    # Update template attributes
    for key, value in form_template.dict(exclude={"fields"}).items():
        setattr(db_template, key, value)

    # Update existing fields and add new ones
    existing_field_ids = set(field.id for field in db_template.fields)
    updated_field_ids = set()

    for field in form_template.fields:
        if field.id and field.id in existing_field_ids:
            # Update existing field
            db_field = next(f for f in db_template.fields if f.id == field.id)
            for key, value in field.dict(exclude={"id", "field_type"}).items():
                setattr(db_field, key, value)
            db_field.field_type = models.FieldType[field.field_type.upper()]
            updated_field_ids.add(field.id)
        else:
            # Add new field
            db_field = models.FormField(
                **field.dict(exclude={"id", "field_type"}),
                field_type=models.FieldType[field.field_type.upper()],
                template_id=db_template.id
            )
            db.add(db_field)

    # Remove fields that are not in the update
    for field in db_template.fields:
        if field.id not in updated_field_ids:
            db.delete(field)

    db.commit()
    db.refresh(db_template)
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
    responses = db.query(models.FormResponse).options(
        joinedload(models.FormResponse.field_values).joinedload(models.FormFieldValue.field),
        joinedload(models.FormResponse.thread)
    ).offset(skip).limit(limit).all()
    
    for response in responses:
        response.thread_id = response.thread.id if response.thread else None
    
    return responses

@router.get("/responses/{response_id}", response_model=schemas.FormResponse)
def get_form_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db.query(models.FormResponse).options(
        joinedload(models.FormResponse.field_values).joinedload(models.FormFieldValue.field),
        joinedload(models.FormResponse.thread)
    ).filter(models.FormResponse.id == response_id).first()
    
    if db_response is None:
        raise HTTPException(status_code=404, detail="Form response not found")
    
    db_response.thread_id = db_response.thread.id if db_response.thread else None
    
    return db_response

@router.delete("/templates/{template_id}", response_model=schemas.FormTemplate)
def delete_form_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Form template not found")
    
    db.delete(db_template)
    db.commit()
    return db_template

@router.delete("/responses/{response_id}", response_model=schemas.FormResponse)
def delete_form_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db.query(models.FormResponse).filter(models.FormResponse.id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Form response not found")
    
    db.delete(db_response)
    db.commit()
    return db_response