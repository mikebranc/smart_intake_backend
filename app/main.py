from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import forms, phone_intake, client_intake, threads
from app import models
from app.database import engine

# Add any other sensitive data as environment variables

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(forms.router, prefix="/forms", tags=["forms"])
app.include_router(phone_intake.router, prefix="/phone", tags=["phone_intake"])
app.include_router(client_intake.router, prefix="/client_intake", tags=["client_intake"])
app.include_router(threads.router, prefix="/threads", tags=["threads"])