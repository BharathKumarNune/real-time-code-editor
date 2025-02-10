from fastapi import FastAPI
from app.auth import router as auth_router
from app.editor import router as editor_router
from app.ai import ai_debug
import socketio
import uuid

# FastAPI setup
app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(editor_router, prefix="/editor", tags=["Editor"])

# Socket.IO setup
sio = socketio.AsyncServer(async_mode="asgi")
app.mount("/ws", socketio.ASGIApp(sio))

@sio.event
async def connect(sid, environ):
    print(f"User {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"User {sid} disconnected")

@sio.event
async def edit_code(sid, data):
    await sio.emit("update_code", data, skip_sid=sid)

@app.get("/")
def root():
    return {"message": "Real-time Code Editor API is running"}

@sio.event
async def request_suggestion(sid, data):
    suggestions = ai_debug(data["code"])
    suggestion_id = str(uuid.uuid4())
    await sio.emit("suggestion_response", {"suggestion_id": suggestion_id, "suggestions": suggestions}, room=sid)
