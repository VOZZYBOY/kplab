from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Appointment
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AppointmentCreate(BaseModel):
    user_id: int
    doctor_id: int
    service_id: int
    appointment_time: datetime

@router.post("/appointments")
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Check for double booking
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_time == appointment.appointment_time
    ).first()
    if existing_appointment:
        raise HTTPException(status_code=400, detail="Appointment time is already booked")

    new_appointment = Appointment(
        user_id=appointment.user_id,
        doctor_id=appointment.doctor_id,
        service_id=appointment.service_id,
        appointment_time=appointment.appointment_time
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return {"message": "Appointment created successfully", "appointment_id": new_appointment.id}

@router.get("/appointments")
async def read_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return appointments

@router.put("/appointments/{appointment_id}")
async def update_appointment(appointment_id: int, appointment: AppointmentCreate, db: Session = Depends(get_db)):
    existing_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not existing_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    existing_appointment.user_id = appointment.user_id
    existing_appointment.doctor_id = appointment.doctor_id
    existing_appointment.service_id = appointment.service_id
    existing_appointment.appointment_time = appointment.appointment_time
    db.commit()
    return {"message": "Appointment updated successfully"}

@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    existing_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not existing_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(existing_appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}
