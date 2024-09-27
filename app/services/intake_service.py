from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langgraph.managed import IsLastStep
from pydantic import BaseModel, Field, create_model
from typing import Dict, Any, List, Optional, Union, Sequence
from typing_extensions import Annotated, TypedDict
from enum import Enum
from datetime import date
from app.models import FormTemplate, FormField, FormResponse, FormFieldValue, Thread
from app.schemas import FieldType
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Data storage (consider using a database in a production environment)
data = {}

class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    is_last_step: IsLastStep

def to_snake_case(string: str) -> str:
    return string.lower().replace(' ', '_')

def get_current_template(db: Session) -> FormTemplate:
    current_template = db.query(FormTemplate).filter(FormTemplate.is_current == True).first()
    if not current_template:
        raise ValueError("No current form template found")
    return current_template

def generate_form_input_class(db: Session) -> type[BaseModel]:
    current_template = get_current_template(db)
    
    fields: Dict[str, Any] = {}
    for field in current_template.fields:
        field_type, field_options = get_pydantic_field_type(field)
        
        description = field.description or ""
        if field.field_type == FieldType.RADIO and field.options:
            enum_values = " | ".join(field.options)
            description += f" Must be one of the following enum values: {enum_values}"
        
        snake_case_name = to_snake_case(field.name)
        
        # All fields are optional
        fields[snake_case_name] = (Optional[field_type], Field(description=description, default=None, **field_options))

    return create_model(f"DynamicFormInput_{current_template.id}", **fields)

def get_pydantic_field_type(field: FormField) -> tuple:
    if field.field_type == FieldType.STRING:
        return (str, {})
    elif field.field_type == FieldType.INTEGER:
        return (int, {})
    elif field.field_type == FieldType.DATE:
        return (date, {})
    elif field.field_type == FieldType.CHECKBOX:
        return (bool, {})
    elif field.field_type == FieldType.RADIO:
        enum_class = Enum(f"{to_snake_case(field.name)}Enum", {opt.lower().replace(' ', '_'): opt for opt in field.options})
        return (enum_class, {})
    else:
        return (str, {})  # Default to string for unknown types

def generate_complete_form_function(db: Session, thread_id: Optional[int] = None):
    current_template = get_current_template(db)

    def complete_form(thread_id: Optional[int] = thread_id,**kwargs) -> Dict[str, Any]:
        form_response = FormResponse(template_id=current_template.id)
        db.add(form_response)
        
        for field in current_template.fields:
            snake_case_name = to_snake_case(field.name)
            value = kwargs.get(snake_case_name)
            if value is not None:
                if isinstance(value, Enum):
                    value = value.value
                elif isinstance(value, date):
                    value = value.isoformat()
                
                field_value = FormFieldValue(field_id=field.id, value=str(value))
                form_response.field_values.append(field_value)
        
        db.commit()

        # Update the thread with the form if thread_id is provided
        if thread_id:
            thread = db.query(Thread).filter(Thread.id == thread_id).first()
            if thread:
                thread.form = form_response
                db.commit()

        return kwargs

    return complete_form

def setup_form_tool(db: Session, thread_id: Optional[int] = None) -> StructuredTool:
    DynamicFormInput = generate_form_input_class(db)
    complete_form_func = generate_complete_form_function(db, thread_id)

    current_template = get_current_template(db)
    form_tool = StructuredTool.from_function(
        func=complete_form_func,
        name=f"Form_Completer_{current_template.id}",
        description="Completes an intake form for the user based on the fields provided in the schema.",
        args_schema=DynamicFormInput,
        return_direct=False,
        handle_tool_error=True,
    )
    return form_tool

# Global variables for model and memory
model = ChatOpenAI(model="gpt-4o")
memory = MemorySaver()
system_prompt = "You are a helpful assistant named Steve required to complete intake forms for clients. Please immediately begin the intake process. Do not ask how to assist them, immediately start asking questions after you greet them. Do not stop asking questions until you've gathered all the information you need as defined in the form_completer tool schema. You previously asked the user how they were doing so be prepared to respond to that first."

def get_agent_executor(db: Session, thread_id: Optional[int] = None):

    form_completer = setup_form_tool(db, thread_id)
    tools = [form_completer]
    return create_react_agent(model, tools, state_modifier=system_prompt, checkpointer=memory)

async def process_message(message: str, db: Session, thread_id: Optional[int] = None):
    config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
    agent_executor = get_agent_executor(db, thread_id)
    response_chunks = []
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content=message)]}, config
    ):
        if isinstance(chunk, dict) and 'agent' in chunk:
            agent_message = chunk['agent']['messages'][0]
            if isinstance(agent_message.content, str):
                response_chunks.append(agent_message.content)
        elif isinstance(chunk, str):
            response_chunks.append(chunk)
    
    return " ".join(response_chunks)

def get_form_responses(thread_id: int, db: Session) -> Dict[str, Any]:
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread or not thread.form:
        return {}

    form_response = thread.form
    template = form_response.template
    
    responses = {}
    for field_value in form_response.field_values:
        field = db.query(FormField).filter(FormField.id == field_value.field_id).first()
        if field:
            responses[field.name] = field_value.value

    return {
        "template_name": template.name,
        "template_description": template.description,
        "responses": responses
    }

def get_form_data(db: Session) -> Dict[str, Any]:
    current_template = get_current_template(db)
    fields = []
    for field in current_template.fields:
        fields.append({
            "name": field.name,
            "description": field.description,
            "field_type": field.field_type,
            "options": field.options,
            "order": field.order
        })
    
    return {
        "template_name": current_template.name,
        "template_description": current_template.description,
        "fields": fields
    }