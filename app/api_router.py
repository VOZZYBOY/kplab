from fastapi import FastAPI
from .api_services import router as services_router
from .api_doctors import router as doctors_router
from .api_appointments import router as appointments_router
from .user_registration import router as registration_router
from .user_login import router as login_router

def include_routers(app: FastAPI):
    app.include_router(registration_router)
    app.include_router(login_router)
    app.include_router(services_router)
    app.include_router(doctors_router)
    app.include_router(appointments_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}
