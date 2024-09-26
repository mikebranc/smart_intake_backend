from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FormFieldBase(BaseModel):
    name: str
    description: Optional[str] = None
    field_type: str
    options: Optional[List[str]] = None
    required: bool = False
    order: int

class FormFieldCreate(FormFieldBase):
    pass

class FormField(FormFieldBase):
    id: int
    template_id: int

    class Config:
        from_attributes = True

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

class FormFieldValueBase(BaseModel):
    field_id: int
    value: str

class FormFieldValueCreate(FormFieldValueBase):
    pass

class FormFieldValue(FormFieldValueBase):
    id: int
    response_id: int

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

    class Config:
        from_attributes = True

class ThreadBase(BaseModel):
    completed: bool = False
    form_id: Optional[int] = None

class ThreadCreate(ThreadBase):
    pass

class Thread(ThreadBase):
    id: int
    created_at: datetime
    updated_at: datetime
    transcript: Optional[str] = None

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
        from_attributes = True