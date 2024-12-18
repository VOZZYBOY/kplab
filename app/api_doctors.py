from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Doctor
from pydantic import BaseModel

router = APIRouter()

class DoctorCreate(BaseModel):
    name: str
    specialty: str
    availability: str

@router.post("/doctors")
async def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    new_doctor = Doctor(name=doctor.name, specialty=doctor.specialty, availability=doctor.availability)
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {"message": "Doctor created successfully", "doctor_id": new_doctor.id}

@router.get("/doctors")
async def read_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return doctors

@router.put("/doctors/{doctor_id}")
async def update_doctor(doctor_id: int, doctor: DoctorCreate, db: Session = Depends(get_db)):
    existing_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    existing_doctor.name = doctor.name
    existing_doctor.specialty = doctor.specialty
    existing_doctor.availability = doctor.availability
    db.commit()
    return {"message": "Doctor updated successfully"}

@router.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    existing_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db.delete(existing_doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}
