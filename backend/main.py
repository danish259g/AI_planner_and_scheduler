from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
from backend.interpreter import interpret_task as interpret_task_logic
from backend.scheduler import orchestrate_schedule

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
    id: Any # Changed to Any to support int/str ids from frontend
    title: str
    duration_mins: int
    status: str = "pending"
    tag: Optional[str] = "General"
    # Scheduling fields
    scheduled_day: Optional[str] = None
    scheduled_hour: Optional[int] = None

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
    """Real interpreter using Gemini."""
    try:
        data = await interpret_task_logic(input.raw_text)
        return Task(
            id=str(random.randint(1000, 9999)),
            title=data.task_name,
            duration_mins=data.duration,
            status="interpreted"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule/generate", response_model=Schedule)
async def generate_schedule(tasks: List[Task]):
    """Real scheduler: calls Gemini to orchestrate."""
    try:
        # Convert Pydantic models to dicts for the scheduler
        task_dicts = [t.dict() for t in tasks]
        
        # Call orchestration logic
        orchestrated_result = await orchestrate_schedule(task_dicts)
        
        # Map the results back to the Task objects
        # We need to map by ID.
        scheduled_map = {str(item.task_id): item for item in orchestrated_result.schedule}
        
        updated_tasks = []
        for t in tasks:
            # Check if this task was scheduled
            matches = scheduled_map.get(str(t.id))
            if matches:
                 t.scheduled_day = matches.day
                 t.scheduled_hour = matches.start_time
                 t.status = "scheduled"
            updated_tasks.append(t)

        return Schedule(
            week_id="week-1",
            tasks=updated_tasks
        )
    except Exception as e:
        print(f"Scheduling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/negotiate", response_model=ChatMessage)
async def negotiate(request: ChatRequest):
    """Dummy negotiator: echoes back a response."""
    return ChatMessage(
        sender="ai",
        message=f"I received your message: '{request.message}'. This is a dummy response from the skeleton."
    )

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
