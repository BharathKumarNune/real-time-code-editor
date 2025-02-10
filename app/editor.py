from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.ai import ai_debug
from app.db import get_db, Suggestion
import uuid

router = APIRouter()

@router.get("/")
def get_code():
    return {"message": "Code editor is active."}

@router.post("/save")
def save_code(code: str):
    return {"message": "Code saved successfully."}

@router.post("/debug")
def debug_code(code: str, db: Session = Depends(get_db)):
    suggestions = ai_debug(code)
    suggestion_id = str(uuid.uuid4())
    new_suggestion = Suggestion(id=suggestion_id, code=code, suggestions=suggestions, status="pending")
    db.add(new_suggestion)
    db.commit()
    return {"message": "AI Suggestions for debugging.", "suggestions": suggestions, "suggestion_id": suggestion_id, "action": "Accept or Reject the suggestions."}

@router.post("/apply_suggestion")
def apply_suggestion(suggestion_id: str, action: str, db: Session = Depends(get_db)):
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Invalid suggestion ID.")
    
    if action.lower() == "accept":
        suggestion.status = "accepted"
        db.commit()
        return {"message": "Suggestion accepted and applied successfully."}
    elif action.lower() == "reject":
        suggestion.status = "rejected"
        db.commit()
        return {"message": "Suggestion rejected."}
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'accept' or 'reject'.")
