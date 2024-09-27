from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"

class FormFieldBase(BaseModel):
    name: str
    description: Optional[str] = None
    field_type: FieldType
    options: Optional[List[str]] = None
    order: int

    @validator('options')
    @classmethod
    def validate_options(cls, v, values):
        if values['field_type'] in [FieldType.RADIO] and not v:
            raise ValueError('Options are required for radio fields')
        return v

class FormFieldCreate(FormFieldBase):
    pass

class FormField(FormFieldBase):
    id: int
    template_id: int

    class Config:
        from_attributes = True

class FormFieldUpdate(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str] = None
    field_type: FieldType
    options: Optional[List[str]] = None
    order: int

class FormTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_current: bool = False

class FormTemplateCreate(FormTemplateBase):
    fields: List[FormFieldCreate]

class FormTemplate(FormTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    fields: List[FormField]

    class Config:
        from_attributes = True

class FormTemplateUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    is_current: Optional[bool] = None
    fields: List[FormFieldUpdate]

class FormFieldValueBase(BaseModel):
    field_id: int
    value: str

class FormFieldValueCreate(FormFieldValueBase):
    pass

class FormFieldValue(FormFieldValueBase):
    id: int
    response_id: int
    field_name: str  # Add this line

    class Config:
        from_attributes = True

class FormResponseBase(BaseModel):
    template_id: int

class FormResponseCreate(FormResponseBase):
    field_values: List[FormFieldValueCreate]

class FormResponse(FormResponseBase):
    id: int
    submitted_at: datetime
    field_values: List[FormFieldValue]
    template_name: str
    thread_id: Optional[int]

    class Config:
        from_attributes = True

class PhoneMessageBase(BaseModel):
    voice_input: str
    assistant_response: str

class PhoneMessageCreate(PhoneMessageBase):
    thread_id: int

class PhoneMessage(PhoneMessageBase):
    id: int
    thread_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ThreadBase(BaseModel):
    completed: bool
    transcript: Optional[str] = None

class ThreadCreate(ThreadBase):
    pass

class Thread(ThreadBase):
    id: int
    created_at: datetime
    form_id: Optional[int] = None
    messages: List["PhoneMessage"] = []

    class Config:
        orm_mode = True

class SetCurrentTemplate(BaseModel):
    is_current: bool = True
