import json
import os
from typing import List, Dict, Any
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database.json'

def _ensure_db():
    if not DB_PATH.exists():
        with open(DB_PATH, 'w') as f:
            json.dump({
                "tasks": [], 
                "user_profile": "",
                "user_settings": {
                    "study_start": 8,
                    "study_end": 22,
                    "constraints": []
                },
                "next_task_id": 1,
                "performance_data": {
                    "Quantitative": {"score": 0, "self_eval": 5, "count": 0},
                    "Verbal": {"score": 0, "self_eval": 5, "count": 0},
                    "English": {"score": 0, "self_eval": 5, "count": 0},
                    "Essay": {"score": 0, "self_eval": 5, "count": 0}
                }
            }, f)

def get_performance() -> Dict[str, Any]:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    # Survival check/migration for existing DBs
    if "performance_data" not in data:
        data["performance_data"] = {
            "Quantitative": {"score": 0, "self_eval": 5, "count": 0},
            "Verbal": {"score": 0, "self_eval": 5, "count": 0},
            "English": {"score": 0, "self_eval": 5, "count": 0},
            "Essay": {"score": 0, "self_eval": 5, "count": 0}
        }
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    return data["performance_data"]

def update_performance(category: str, score: float, self_eval: int):
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    if "performance_data" not in data:
        data["performance_data"] = {}
        
    perf = data["performance_data"].get(category, {"score": 0, "self_eval": 5, "count": 0})
    
    # Calculate new average score if it's a new result
    if score is not None:
        current_total = perf["score"] * perf["count"]
        perf["count"] += 1
        perf["score"] = (current_total + score) / perf["count"]
    
    if self_eval is not None:
        perf["self_eval"] = self_eval
        
    data["performance_data"][category] = perf
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    return data["performance_data"]

def reset_performance():
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    data["performance_data"] = {
        "Quantitative": {"score": 0, "self_eval": 5, "count": 0},
        "Verbal": {"score": 0, "self_eval": 5, "count": 0},
        "English": {"score": 0, "self_eval": 5, "count": 0},
        "Essay": {"score": 0, "self_eval": 5, "count": 0}
    }
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    return data["performance_data"]

def load_tasks() -> List[Dict[str, Any]]:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    tasks = data.get("tasks", [])
    
    # MIGRATION: 
    # If tasks have old 'scheduled_hour' but missing 'scheduled_start', convert them.
    # We do this on load so the app always sees the new schema.
    has_changes = False
    for t in tasks:
        if "scheduled_hour" in t:
            if t.get("scheduled_start") is None:
                t["scheduled_start"] = t["scheduled_hour"]
                # Infer end
                duration_hrs = t.get("duration", 30) / 60
                t["scheduled_end"] = t["scheduled_hour"] + duration_hrs
                has_changes = True
            
            # Remove old key
            del t["scheduled_hour"]
            has_changes = True
            
    if has_changes:
        save_tasks(tasks)
        
    return tasks

def save_tasks(tasks: List[Dict[str, Any]]):
    _ensure_db()
    # Read existing data to preserve user_profile
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    data["tasks"] = tasks
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def add_task(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Read fresh
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    tasks = data.get("tasks", [])
    next_id = data.get("next_task_id", 1)
    
    # Check if this is an update (task has ID and exists)
    t_id = str(task.get("id", ""))
    existing_index = -1
    if t_id:
        existing_index = next((i for i, t in enumerate(tasks) if str(t.get("id")) == t_id), -1)
    
    if existing_index >= 0:
        tasks[existing_index] = task
    else:
        # New Task - Assign ID
        task["id"] = str(next_id)
        data["next_task_id"] = next_id + 1
        tasks.append(task)
        
    data["tasks"] = tasks
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
        
    return tasks

def delete_task(task_id: str) -> List[Dict[str, Any]]:
    tasks = load_tasks()
    tasks = [t for t in tasks if str(t.get("id")) != str(task_id)]
    save_tasks(tasks)
    return tasks

def clear_schedule_data() -> List[Dict[str, Any]]:
    tasks = load_tasks()
    for t in tasks:
        if "scheduled_day" in t:
            del t["scheduled_day"]
        if "scheduled_start" in t:
            del t["scheduled_start"]
        if "scheduled_end" in t:
            del t["scheduled_end"]
        t["status"] = "pending"
    save_tasks(tasks)
    return tasks

def get_user_profile() -> str:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    return data.get("user_profile", "")

def update_user_profile(profile_text: str) -> str:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    data["user_profile"] = profile_text
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
        
    return profile_text

def get_user_settings() -> Dict[str, Any]:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    if "user_settings" not in data:
        data["user_settings"] = {
            "study_start": 8,
            "study_end": 22,
            "constraints": []
        }
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
            
    return data["user_settings"]

def update_user_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())
    
    data["user_settings"] = settings
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
        
    return settings
