from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
from backend.interpreter import interpret_task as interpret_task_logic
from backend.scheduler import orchestrate_schedule
from backend.verifier import verify_schedule_algorithmic
import backend.storage as storage

app = FastAPI(title="AI Weekly Planner Backend") # Reload trigger

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class TaskInput(BaseModel):
    raw_text: str

# Updated Task model matching interpreter
class Task(BaseModel):
    id: Any
    name: str # Renamed from title
    duration: int # Renamed from duration_mins to match interpreter
    status: str = "pending"
    # New Fields
    tag: Optional[str] = "General"
    location: Optional[str] = "Home" 
    priority: Optional[str] = "Medium"
    is_locked: bool = False
    day: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    comments: Optional[str] = ""
    # Scheduling fields
    scheduled_day: Optional[str] = None
    scheduled_hour: Optional[int] = None

class Schedule(BaseModel):
    week_id: str
    tasks: List[Task]
    warnings: List[str] = []
    logic_summary: Optional[str] = ""

class ChatMessage(BaseModel):
    sender: str
    message: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "AI Planner Backend is running"}

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    # Helper to map old DB format if needed, though we should clear DB for fresh start ideally
    raw_tasks = storage.load_tasks()
    # Ensure they match the schema (e.g. rename title -> name if old data exists)
    clean_tasks = []
    for t in raw_tasks:
        if "title" in t and "name" not in t:
            t["name"] = t.pop("title")
        if "duration_mins" in t and "duration" not in t:
            t["duration"] = t.pop("duration_mins")
        clean_tasks.append(t)
    return clean_tasks

@app.post("/api/tasks", response_model=Task)
async def add_task(task: Task):
    # In a real app we might validate or generate ID backend-side if not provided
    # For now we trust the frontend or storage wrapper
    storage.add_task(task.dict())
    return task

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    storage.delete_task(task_id)
    return {"status": "success"}

@app.post("/api/interpret", response_model=Task)
async def interpret_task(input: TaskInput):
    """Real interpreter using Gemini."""
    try:
        data = await interpret_task_logic(input.raw_text)
        return Task(
            id=str(random.randint(1000, 9999)), 
            name=data.name,
            duration=data.duration,
            tag=data.tag,
            location=data.location,
            priority=data.priority,
            is_locked=data.is_locked,
            day=data.day,
            start_time=data.start_time,
            end_time=data.end_time,
            comments=data.comments,
            status="interpreted"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule/generate", response_model=Schedule)
async def generate_schedule(): # No payload needed, reads from DB
    """Real scheduler: calls Gemini to orchestrate tasks from DB."""
    try:
        # 1. Load tasks from DB
        raw_tasks = storage.load_tasks()
        
        # Normalize keys for Orchestrator
        current_tasks = []
        for t in raw_tasks:
             # Normalize for the scheduler input which expects specific keys or handles fallbacks
             # Ensure 'name' and 'duration' exist
             if "title" in t and "name" not in t: t["name"] = t["title"]
             if "duration_mins" in t and "duration" not in t: t["duration"] = t["duration_mins"]
             current_tasks.append(t)

        
        # 2. Orchestrate (only pending or all? Let's do all for now to re-optimize)
        orchestrated_result = await orchestrate_schedule(current_tasks)
        
        # 3. Verify
        warnings = verify_schedule_algorithmic(orchestrated_result)
        if warnings:
            print("Scheduling Warnings:", warnings)
        
        # 4. Update tasks with schedule info
        scheduled_map = {str(item.task_id): item for item in orchestrated_result.schedule}
        
        updated_tasks = []
        for t in current_tasks:
            # We are working with dicts from storage
            t_id = str(t.get("id"))
            matches = scheduled_map.get(t_id)
            if matches:
                 t["scheduled_day"] = matches.day
                 t["scheduled_hour"] = matches.start_time
                 t["status"] = "scheduled"
            updated_tasks.append(t)
            
        # 5. Save back to DB
        storage.save_tasks(updated_tasks)

        return Schedule(
            week_id=str(random.randint(10000, 99999)),
            tasks=updated_tasks,
            warnings=warnings,
            logic_summary=orchestrated_result.logic_summary
        )
    except Exception as e:
        print(f"Scheduling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule/clear", response_model=Schedule)
async def clear_schedule():
    app.state.tasks = storage.clear_schedule_data()
    return Schedule(
        week_id="week-1",
        tasks=app.state.tasks
    )

@app.post("/api/chat/negotiate", response_model=ChatMessage)
async def negotiate(request: ChatRequest):
    """Dummy negotiator: echoes back a response."""
    return ChatMessage(
        sender="ai",
        message=f"I received your message: '{request.message}'. This is a dummy response from the skeleton."
    )

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
