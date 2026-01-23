from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
from pathlib import Path
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
    scheduled_start: Optional[float] = None # Hour 0-23
    scheduled_end: Optional[float] = None # Hour 0-24

class UserProfile(BaseModel):
    profile: str

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
    history: Optional[List[ChatMessage]] = None

class PerformanceUpdate(BaseModel):
    category: str
    score: Optional[float] = None
    self_eval: Optional[int] = None

# --- Endpoints ---

@app.get("/api/performance")
async def get_performance():
    return storage.get_performance()

@app.post("/api/performance")
async def update_performance(data: PerformanceUpdate):
    return storage.update_performance(data.category, data.score, data.self_eval)

@app.post("/api/performance/reset")
async def reset_performance():
    return storage.reset_performance()

@app.get("/api/settings")
async def get_settings():
    return storage.get_user_settings()

@app.post("/api/settings")
async def update_settings(settings: Dict[str, Any]):
    return storage.update_user_settings(settings)

@app.get("/")
async def root():
    return {"message": "AI Planner Backend is running"}

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    print("DEBUG: Fetching tasks from storage...")
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
        new_task = Task(
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
        
        # Save to DB immediately so it shows up in the UI/Task Bank
        storage.add_task(new_task.dict())
        
        return new_task
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

        # Filter for pending tasks - REMOVED. We want to re-orchestrate the whole week.
        # pending_tasks = [t for t in current_tasks if t.get("status") == "pending"]
        # if not pending_tasks:
        #     # If no pending tasks, return current tasks as is
        #     return Schedule(week_id="empty", tasks=current_tasks)

        # Get Performance Data
        user_profile = storage.get_user_profile()
        perf_data = storage.get_performance()
        user_settings = storage.get_user_settings()

        # 2. Orchestrate - Send ALL current tasks to allow re-optimization of the whole week
        # The 'is_locked' flag will protect tasks that shouldn't move.
        orchestrated_result = await orchestrate_schedule(current_tasks, user_profile, performance_data=perf_data, user_settings=user_settings)
        
        # --- LOG THOUGHT PROCESS ---
        log_path = Path(__file__).parent / 'scheduler_thoughts.txt'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n--- Orchestration Run (Generate) ---\n")
            if orchestrated_result.thought_process:
                for step in orchestrated_result.thought_process:
                    f.write(f"> {step}\n")
            else:
                f.write("(No thought process returned)\n")
        # ---------------------------
        
        # 3. Verify
        warnings = verify_schedule_algorithmic(orchestrated_result)
        if warnings:
            print("Scheduling Warnings:", warnings)
        
        # 4. Update tasks with schedule info
        scheduled_map = {str(item.task_id): item for item in orchestrated_result.schedule}
        
        updated_tasks = []
        for t in current_tasks: # Iterate through all tasks, not just pending
            # We are working with dicts from storage
            t_id = str(t.get("id"))
            matches = scheduled_map.get(t_id)
            if matches:
                 t["scheduled_day"] = matches.day
                 t["scheduled_start"] = matches.start_time
                 # Calculate end time from duration
                 duration_hours = t.get("duration", 30) / 60
                 t["scheduled_end"] = matches.start_time + duration_hours
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
        if str(e) == "GEMINI_OVERLOADED":
            raise HTTPException(status_code=503, detail="The AI Scheduler is currently overloaded (Google API 503). Please try again in a few seconds.")
        print(f"Scheduling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile")
def get_profile():
    return {"profile": storage.get_user_profile()}

@app.post("/api/profile")
def update_profile(data: UserProfile):
    storage.update_user_profile(data.profile)
    return {"status": "updated", "profile": data.profile}

@app.post("/api/negotiate", response_model=Schedule)
async def negotiate_schedule(request: ChatRequest):
    """Refine schedule based on user chat message"""
    try:
        # 2. Fetch all tasks to give AI context
        all_tasks = storage.load_tasks()
        user_profile = storage.get_user_profile()
        perf_data = storage.get_performance()
        user_settings = storage.get_user_settings()

        # 3. Orchestrate with Feedback
        orchestrated_result = await orchestrate_schedule(
            all_tasks, 
            user_profile, 
            user_feedback=request.message,
            performance_data=perf_data,
            user_settings=user_settings
        )
  # --- LOG THOUGHT PROCESS ---
        log_path = Path(__file__).parent / 'scheduler_thoughts.txt'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n--- Orchestration Run (Negotiate) ---\n")
            f.write(f"User Feedback: {request.message}\n")
            if orchestrated_result.thought_process:
                for step in orchestrated_result.thought_process:
                    f.write(f"> {step}\n")
            else:
                f.write("(No thought process returned)\n")
        # ---------------------------
        
        # Verify
        warnings = verify_schedule_algorithmic(orchestrated_result)
        
        # 4. Update DB
        updated_tasks = []
        scheduled_map = {str(item.task_id): item for item in orchestrated_result.schedule}

        for t in all_tasks:
            t_id = str(t.get("id"))
            matches = scheduled_map.get(t_id)
            if matches:
                t["scheduled_day"] = matches.day
                t["scheduled_start"] = matches.start_time
                t["scheduled_end"] = matches.start_time + (t.get("duration", 30) / 60)
                t["status"] = "scheduled"
            updated_tasks.append(t)
        
        # Save updates
        storage.save_tasks(updated_tasks)
        
        return Schedule(
            week_id=str(random.randint(10000, 99999)),
            tasks=updated_tasks,
            warnings=warnings,
            logic_summary=orchestrated_result.logic_summary
        )

    except Exception as e:
        if str(e) == "GEMINI_OVERLOADED":
            raise HTTPException(status_code=503, detail="The AI Scheduler is currently overloaded (Google API 503). Please try again in a few seconds.")
        print(f"Negotiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule/clear", response_model=Schedule)
async def clear_schedule():
    tasks = storage.clear_schedule_data()
    return Schedule(
        week_id="cleared",
        tasks=tasks
    )



if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
