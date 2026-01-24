import asyncio
import os
import json
from datetime import datetime
from backend.scheduler import orchestrate_schedule

# Mock Data
mock_tasks = [
    {"id": "1", "name": "Hard Geometry Problems", "tag": "Quantitative", "duration": 45, "priority": "High"},
    {"id": "2", "name": "Write Argumentative Essay", "tag": "Essay", "duration": 60, "priority": "High"},
]

mock_settings = {
    "study_start": 8, "study_end": 22, "max_daily_hours": 4, "peak_energy": "morning", "constraints": []
}

async def run_verification():
    print("\n--- RUN 1: Cold Start (Expect Profiling) ---")
    
    # 1. First Run
    result1 = await orchestrate_schedule(
        events=mock_tasks,
        user_profile="Student",
        user_settings=mock_settings
    )
    
    print(f"Run 1 Logic: {result1.thought_process}")
    
    if not hasattr(result1, 'task_profiles') or not result1.task_profiles:
        print("❌ FAILED: No task_profiles returned in Run 1")
        return
    
    print(f"✅ Run 1 Profiles: {result1.task_profiles}")

    # 2. Simulate Persistence
    print("\n--- RUN 2: Warm Start (Expect SKIPPING Profiling) ---")
    updated_tasks = []
    for t in mock_tasks:
        t_copy = t.copy()
        if t["id"] in result1.task_profiles:
            t_copy["cognitive_type"] = result1.task_profiles[t["id"]]
        updated_tasks.append(t_copy)
        
    print(f"Input for Run 2 (First task has type?): {updated_tasks[0].get('cognitive_type')}")
    
    # 3. Second Run
    result2 = await orchestrate_schedule(
        events=updated_tasks,
        user_profile="Student",
        user_settings=mock_settings
    )
    
    # We can't automatically assert Console Output here, but the user can see it.
    # However, we can check if result2 still has the profiles (from cache)
    if result2.task_profiles == result1.task_profiles:
        print("✅ PASSED: Profiles preserved in Run 2 output.")
    else:
        print("❌ FAILED: Profiles lost or changed in Run 2.")

if __name__ == "__main__":
    asyncio.run(run_verification())
