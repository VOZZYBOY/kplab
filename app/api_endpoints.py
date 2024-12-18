from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.yandex_gpt import process_query  # Import the chatbot function

router = APIRouter()

# Existing endpoints...

@router.post("/chatbot")
async def chatbot(query: str, db: Session = Depends(get_db)):
    folder_id = "b1gb9k14k5ui80g91tnp"  # Replace with your actual folder ID
    # Ensure the query is validated before processing
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    response = process_query(query, folder_id, db)
    return {"response": response}
