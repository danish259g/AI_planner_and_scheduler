import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except UnicodeDecodeError:
    load_dotenv(dotenv_path=env_path, encoding='utf-16')

class OrchestratedTask(BaseModel):
    task_id: Any = Field(description="The ID of the task being scheduled")
    day: str = Field(description="Day of the week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)")
    start_time: int = Field(description="Start hour (0-23)")
    duration_mins: int = Field(description="Duration in minutes")
    rationale: Optional[str] = Field(description="Brief reason for this slot (e.g. 'Bundled with other errands', 'High energy morning slot')")

class WeeklySchedule(BaseModel):
    schedule: List[OrchestratedTask]
    logic_summary: str = Field(description="A brief explanation of how you solved the schedule, highlighting any compromises, bundles, or trade-offs made.")

async def orchestrate_schedule(tasks: List[Dict[str, Any]], user_profile: str = "", user_feedback: str = None) -> WeeklySchedule:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Convert tasks to a cleaner format for the LLM
    # We strip out implementation details and send the rich semantic fields
    clean_tasks = []
    for t in tasks:
        clean_tasks.append({
            "id": t["id"],
            "name": t.get("name"),
            "duration": t.get("duration"),
            "priority": t.get("priority"),
            "is_locked": t.get("is_locked"),
            "day": t.get("day"), # Fixed day if locked
            "start_time": t.get("start_time"), # Fixed time if locked
            "end_time": t.get("end_time"),
            "comments": t.get("comments", ""),
            # Include current schedule state for context
            "current_day": t.get("scheduled_day"),
            "current_start": t.get("scheduled_start"),
            "current_end": t.get("scheduled_end")
        })

    task_list_str = json.dumps(clean_tasks, indent=2)

    prompt = f"""
    You are an expert AI Scheduler. Your goal is to create an optimal weekly schedule for the user.
    
    [USER VIBE & PREFERENCES]
    The user has a specific working style and set of preferences. You MUST respect these as soft constraints.
    Maximize the user's satisfaction by aligning the schedule with this "Vibe":
    "{user_profile}"
    
    [INPUT TASKS]
    {task_list_str}


    Instruction:
    - If User Feedback is provided, modify the current schedule to satisfy the request.
    - Keep other tasks in their current slots if possible to maintain stability, unless they need to move to accommodate the request.
    
    Output:
    - Return a JSON object matching the WeeklySchedule schema.
    - 'start_time' should be an integer hour (0-23).
    - **logic_summary**: Be extremely concise. Only mention key trade-offs or bundles if absolutely necessary. If the schedule is straightforward, just say "Schedule updated." or "Optimized for flow." (Max 1 short sentence).
    """

    # Single shot orchestration as per plan (no retry loop for now)
    # Single shot execution (No retries)
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': WeeklySchedule
            }
        )

        if response.parsed:
            return response.parsed
        
        data = json.loads(response.text)
        return WeeklySchedule(**data)

    except Exception as e:
        error_msg = str(e).lower()
        if "503" in error_msg or "overloaded" in error_msg or "resource exhausted" in error_msg:
            print(f"Gemini API Overloaded: {e}")
            raise ValueError("GEMINI_OVERLOADED")
        
        print(f"Error during orchestration: {e}")
        raise e
