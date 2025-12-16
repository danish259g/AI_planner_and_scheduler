from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random

app = FastAPI(title="AI Weekly Planner Backend (Skeleton)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dummy Models ---
class TaskInput(BaseModel):
    raw_text: str

class Task(BaseModel):
    id: str
    title: str
    duration_mins: int
    status: str = "pending"

class Schedule(BaseModel):
    week_id: str
    tasks: List[Task]

class ChatMessage(BaseModel):
    sender: str
    message: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

# --- Dummy Endpoints ---

@app.get("/")
async def root():
    return {"message": "AI Planner Backend is running"}

@app.post("/api/interpret", response_model=Task)
async def interpret_task(input: TaskInput):
    """Dummy interpreter: returns a structured task from text."""
    return Task(
        id=str(random.randint(1000, 9999)),
        title=input.raw_text,
        duration_mins=60,
        status="interpreted"
    )

@app.post("/api/schedule/generate", response_model=Schedule)
async def generate_schedule(tasks: List[Task]):
    """Dummy scheduler: returns a fake schedule."""
    # Assign dummy time slots if needed, or just return list
    return Schedule(
        week_id="week-1",
        tasks=tasks
    )

@app.post("/api/chat/negotiate", response_model=ChatMessage)
async def negotiate(request: ChatRequest):
    """Dummy negotiator: echoes back a response."""
    return ChatMessage(
        sender="ai",
        message=f"I received your message: '{request.message}'. This is a dummy response from the skeleton."
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
