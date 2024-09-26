from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()


# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Data storage (consider using a database in a production environment)
data = {}

class CompleteFormInput(BaseModel):
    client_name: str = Field(description="client's name")
    email: str = Field(description="client's email")
    phone: str = Field(description="client's phone number")

def completeForm(client_name: str, email: str, phone: str) -> dict:
    """Complete the form for the individual based on their user info"""
    data['client_name'] = client_name
    data['email'] = email
    data['phone'] = phone
    return {
        'client_name': client_name,
        'email': email,
        'phone': phone
    }

form_completer = StructuredTool.from_function(
    func=completeForm,
    name="Form_Completer",
    description="Completes form for the user based on their info",
    args_schema=CompleteFormInput,
    return_direct=False,
    handle_tool_error=True,
)

tools = [form_completer]

model = ChatOpenAI(model="gpt-4o")
model_with_tools = model.bind_tools(tools)

memory = MemorySaver()
system_prompt = "You are a helpful assistant named Steve required to complete intake forms for clients. Please greet the client and immediately begin the intake process. Do not ask how to assist them, immediately start asking questions after you greet them."
agent_executor = create_react_agent(model, tools, state_modifier=system_prompt, checkpointer=memory)

class IntakeService:
    @staticmethod
    async def process_message(message: str, config: dict = None):
        if config is None:
            config = {"configurable": {"thread_id": "abc123"}}
        
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

    @staticmethod
    def get_form_data():
        return data