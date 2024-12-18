from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Service
from pydantic import BaseModel

router = APIRouter()

class ServiceCreate(BaseModel):
    name: str
    description: str

@router.post("/services")
async def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    new_service = Service(name=service.name, description=service.description)
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"message": "Service created successfully", "service_id": new_service.id}

@router.get("/services")
async def read_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services

@router.put("/services/{service_id}")
async def update_service(service_id: int, service: ServiceCreate, db: Session = Depends(get_db)):
    existing_service = db.query(Service).filter(Service.id == service_id).first()
    if not existing_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    existing_service.name = service.name
    existing_service.description = service.description
    db.commit()
    return {"message": "Service updated successfully"}

@router.delete("/services/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db)):
    existing_service = db.query(Service).filter(Service.id == service_id).first()
    if not existing_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(existing_service)
    db.commit()
    return {"message": "Service deleted successfully"}
