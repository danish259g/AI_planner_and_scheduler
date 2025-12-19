
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from backend.scheduler import orchestrate_schedule

# Load env from backend/.env
env_path = Path(__file__).parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except UnicodeDecodeError:
    load_dotenv(dotenv_path=env_path, encoding='utf-16')

async def test_manual_orchestration():
    tasks = [
        {"id": 1, "title": "Buy groceries", "duration_mins": 60, "tag": "Errand"},
        {"id": 2, "title": "Team Meeting", "duration_mins": 45, "tag": "Work"},
        {"id": 3, "title": "Gym", "duration_mins": 90, "tag": "Health"},
    ]
    
    print("Sending tasks to scheduler...")
    try:
        schedule = await orchestrate_schedule(tasks)
        print("\n--- Scheduler Output ---")
        for item in schedule.schedule:
             print(f"Task ID {item.task_id}: {item.day} at {item.start_time}:00 ({item.duration_mins}m)")
        print("\nTest passed!")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_manual_orchestration())
