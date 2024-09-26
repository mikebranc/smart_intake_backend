from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import functions
from app.database import Base
from datetime import datetime, timezone

class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=functions.now())
    updated_at = Column(DateTime(timezone=True), onupdate=functions.now())
    completed = Column(Boolean, default=False)
    form_id = Column(Integer, ForeignKey("form_responses.id"), unique=True, nullable=True)
    form = relationship("FormResponse", back_populates="thread")  # One-to-one relationship
    messages = relationship("PhoneMessage", back_populates="thread")
    transcript = Column(Text, nullable=True)

class PhoneMessage(Base):
    __tablename__ = "phone_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.id"))
    voice_input = Column(String)
    assistant_response = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=functions.now())
    thread = relationship("Thread", back_populates="messages")

class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    fields = relationship("FormField", back_populates="template", cascade="all, delete-orphan")
    responses = relationship("FormResponse", back_populates="template")

class FormField(Base):
    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("form_templates.id"))
    name = Column(String)
    description = Column(String, nullable=True)
    field_type = Column(String)
    options = Column(JSON, nullable=True)
    required = Column(Boolean, default=False)
    order = Column(Integer)
    template = relationship("FormTemplate", back_populates="fields")

class FormResponse(Base):
    __tablename__ = "form_responses"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("form_templates.id"))
    submitted_at = Column(DateTime(timezone=True), server_default=functions.now())
    template = relationship("FormTemplate", back_populates="responses")
    field_values = relationship("FormFieldValue", back_populates="response", cascade="all, delete-orphan")
    thread = relationship("Thread", back_populates="form", uselist=False)  # One-to-one relationship

class FormFieldValue(Base):
    __tablename__ = "form_field_values"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("form_responses.id"))
    field_id = Column(Integer, ForeignKey("form_fields.id"))
    value = Column(String)
    response = relationship("FormResponse", back_populates="field_values")
    field = relationship("FormField")
