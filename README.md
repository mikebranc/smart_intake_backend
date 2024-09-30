# Smart Intake Backend

This project is the backend for a smart intake application that allows users to set up intake form templates and complete them over the phone. It uses FastAPI, leveraging Twilio, Langchain, and OpenAI to provide an intelligent, voice-based form completion experience.

🔗 [Frontend Repository](https://github.com/mikebranc/smart_intake_frontend)
🔗 [Demo](https://drive.google.com/file/d/1OS5fySWRzfcBmNQKfG8dr0uR5Ryydpm2/view?usp=drive_link)
<br/>

## Features

- RESTful API for managing intake form templates
- Voice-based form completion over the phone using Twilio
- AI-powered conversation flow using OpenAI and Langchain
- PostgreSQL Database integration for storing form templates, responses, and conversation threads
- Asynchronous processing of voice inputs

## Application Structure

1. **Main Application** (`app/main.py`)
   - FastAPI application setup
   - CORS middleware configuration
   - Router inclusion for different modules

2. **Form Management** (`app/routers/forms.py`)
   - CRUD operations for form templates
   - Endpoints for creating and retrieving form responses

3. **Phone Intake** (`app/routers/phone_intake.py`)
   - Twilio integration for handling phone calls
   - Voice response generation
   - Handling of speech input

4. **Client Intake** (`app/routers/client_intake.py`)
   - Chat endpoint for processing messages
   - Retrieval of form data
   - currently broken, but allows for testing of agent without having to call phone number

5. **Thread Management** (`app/routers/threads.py`)
   - Endpoints for managing conversation threads
   - Retrieval of thread messages

6. **Intake Service** (`app/services/intake_service.py`)
   - AI-powered message processing using Langchain and OpenAI
   - Dynamic form generation based on templates
   - Form completion logic

7. **Data Models** (`app/models.py`)
   - SQLAlchemy ORM models for database tables

8. **Schemas** (`app/schemas.py`)
   - Pydantic models for request/response validation

## Key Components

- FastAPI for building the RESTful API
- SQLAlchemy for database ORM
- Pydantic for data validation
- Twilio for phone call handling
- Langchain and OpenAI for AI-powered conversations

## Getting Started

To run this project locally:

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add the following variables:
     ```
     OPENAI_API_KEY=<your_openai_api_key>
     TWILIO_ACCOUNT_SID=<your_twilio_account_sid>
     TWILIO_AUTH_TOKEN=<your_twilio_auth_token>
     TWILIO_PHONE_NUMBER=<your_twilio_phone_number>
     DATABASE_URL=<your_database_url>
     ```
4. Run the FastAPI server: `uvicorn app.main:app --reload`

Make sure to also set up and run the frontend server. Refer to the [frontend repository](https://github.com/mikebranc/smart_intake_frontend) for instructions.

## API Endpoints

- `/forms`: Form template and response management
- `/phone`: Phone intake handling
- `/client_intake`: Client chat processing
- `/threads`: Conversation thread management

For a complete list of endpoints and their descriptions, run the server and visit `/docs` for the Swagger UI documentation.

## Database Setup

This project uses SQLAlchemy with PostgreSQL. Make sure to set up your database and update the `DATABASE_URL` in your `.env` file.

## Future Improvements

- Implement user authentication and authorization
- Add more robust error handling and logging
- Implement WebSocket for real-time updates
- Enhance AI model training for more accurate responses
- Add unit and integration tests
- Implement caching for frequently accessed data
- Optimize database queries for better performance
