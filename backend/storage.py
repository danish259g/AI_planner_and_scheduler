import json
import os
from typing import List, Dict, Any
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database.json'

def _ensure_db():
    if not DB_PATH.exists():
        with open(DB_PATH, 'w') as f:
            json.dump({"tasks": []}, f)

def load_tasks() -> List[Dict[str, Any]]:
    _ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.load(f)
    return data.get("tasks", [])

def save_tasks(tasks: List[Dict[str, Any]]):
    with open(DB_PATH, 'w') as f:
        json.dump({"tasks": tasks}, f, indent=2)

def add_task(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    tasks = load_tasks()
    # Check if exists
    existing_index = next((i for i, t in enumerate(tasks) if str(t.get("id")) == str(task.get("id"))), -1)
    
    if existing_index >= 0:
        tasks[existing_index] = task
    else:
        tasks.append(task)
        
    save_tasks(tasks)
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
        if "scheduled_hour" in t:
            del t["scheduled_hour"]
        t["status"] = "pending"
    save_tasks(tasks)
    return tasks
