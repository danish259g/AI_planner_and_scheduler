import asyncio
import os
import sys
from backend.interpreter import interpret_task
from backend.scheduler import orchestrate_schedule
from backend.verifier import verify_schedule_algorithmic
from backend.main import Task

async def test_pipeline():
    print("--- Starting Phase 1 Verification ---")
    
    # 1. Test Interpretation
    input_text = "Go to the gym for a power workout at 5pm urgent"
    print(f"\n1. Testing Interpreter with input: '{input_text}'")
    try:
        task_data = await interpret_task(input_text)
        print("Interpreted Data:")
        print(task_data.model_dump_json(indent=2))
        
        # Verify specific fields
        assert task_data.name, "Name missed"
        assert task_data.location.lower() in ["gym", "health"], f"Unexpected location: {task_data.location}"
        assert task_data.is_locked == True, "Should be locked due to 'at 5pm'"
        assert task_data.priority.lower() in ["high", "urgent"], f"Priority {task_data.priority} not high"
        
    except Exception as e:
        print(f"Interpreter Failed: {e}")
        return

    # 2. Test Scheduler & Verifier
    print("\n2. Testing Scheduler & Verifier")
    
    # Mocking a list of tasks including the one above
    tasks_to_schedule = [
        {
            "id": "1", 
            "name": "Morning Meeting", 
            "duration": 60, 
            "tag": "Work", 
            "location": "Office", 
            "priority": "High", 
            "is_locked": True, 
            "comments": "at 9am" 
        },
        {
            "id": "2", 
            "name": task_data.name, 
            "duration": task_data.duration, 
            "tag": task_data.tag, 
            "location": task_data.location, 
            "priority": task_data.priority, 
            "is_locked": task_data.is_locked, 
            "comments": task_data.comments
        },
        {
            "id": "3",
            "name": "Buy milk",
            "duration": 30,
            "tag": "Errand",
            "location": "Supermarket",
            "priority": "Low",
            "is_locked": False,
            "comments": ""
        },
        # Intentionally overlapping task to test Verifier? 
        # Let's see if the scheduler is smart enough to avoid it first.
    ]
    
    try:
        schedule_result = await orchestrate_schedule(tasks_to_schedule)
        print("Generated Schedule:")
        print(schedule_result.model_dump_json(indent=2))
        
        # 3. Validation
        print("\n3. Running Algorithmic Verifier...")
        errors = verify_schedule_algorithmic(schedule_result)
        if errors:
            print("Verifier Found Issues (Expected if scheduler messed up, or ignore if minor):")
            for e in errors:
                print(f" - {e}")
        else:
            print("Verifier: Schedule passed all checks! (No overlaps, valid times)")

    except Exception as e:
        print(f"Scheduler Failed: {e}")

if __name__ == "__main__":
    # Ensure we can import backend modules (since script is in root effectively)
    sys.path.append(os.getcwd())
    asyncio.run(test_pipeline())
