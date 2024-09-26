from fastapi import FastAPI
from app.routers import phone_intake, client_intake, forms
from app.database import engine
from app import models

# Add any other sensitive data as environment variables

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(phone_intake.router, prefix="/phone", tags=["phone"])
app.include_router(client_intake.router, prefix="/client", tags=["client"])
app.include_router(forms.router, prefix="/forms", tags=["forms"])