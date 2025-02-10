import socketio
import uuid
from app.ai import ai_debug
from app.db import get_db, Suggestion
from sqlalchemy.orm import Session

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"User {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"User {sid} disconnected")

@sio.event
async def edit_code(sid, data):
    """ Broadcast edited code to all users except sender """
    await sio.emit("update_code", data, skip_sid=sid)

@sio.event
async def request_suggestion(sid, data):
    """ AI Suggestion Request - User requests AI help on code """
    code = data.get("code", "")
    if not code:
        await sio.emit("error", {"message": "No code provided"}, room=sid)
        return

    suggestions = ai_debug(code)  # AI Debugging
    suggestion_id = str(uuid.uuid4())

    # Save suggestion in database
    db: Session = next(get_db())
    new_suggestion = Suggestion(id=suggestion_id, code=code, suggestions=suggestions, status="pending")
    db.add(new_suggestion)
    db.commit()
    db.close()

    # Emit AI suggestions back to user
    await sio.emit("suggestion_response", {"suggestion_id": suggestion_id, "suggestions": suggestions}, room=sid)

@sio.event
async def apply_suggestion(sid, data):
    """ Handle user accepting or rejecting AI suggestions """
    suggestion_id = data.get("suggestion_id")
    action = data.get("action")

    db: Session = next(get_db())
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()

    if not suggestion:
        await sio.emit("error", {"message": "Invalid suggestion ID"}, room=sid)
        return

    if action.lower() == "accept":
        suggestion.status = "accepted"
        db.commit()
        await sio.emit("suggestion_applied", {"message": "Suggestion accepted and applied."}, room=sid)
    elif action.lower() == "reject":
        suggestion.status = "rejected"
        db.commit()
        await sio.emit("suggestion_rejected", {"message": "Suggestion rejected."}, room=sid)
    else:
        await sio.emit("error", {"message": "Invalid action. Use 'accept' or 'reject'."}, room=sid)

    db.close()
