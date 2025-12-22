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

async def orchestrate_schedule(tasks: List[Dict[str, Any]]) -> WeeklySchedule:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Convert tasks to a cleaner format for the LLM
    # We strip out implementation details and send the rich semantic fields
    clean_tasks = []
    for t in tasks:
        clean_tasks.append({
            "id": t.get("id"),
            "name": t.get("name", t.get("title")), # key fallback
            "duration": t.get("duration", t.get("duration_mins", 30)),
            "tag": t.get("tag", "General"),
            "location": t.get("location", "Unknown"),
            "priority": t.get("priority", "Medium"),
            "is_locked": t.get("is_locked", False),
            "comments": t.get("comments", "")
        })

    task_list_str = json.dumps(clean_tasks, indent=2)

    prompt = f"""
    You are an intelligent weekly scheduler. Your goal is to assign the following tasks to efficient time slots in a weekly calendar.
    
    Tasks:
    {task_list_str}

    Global Constraints:
    - The week days are: Mon, Tue, Wed, Thu, Fri, Sat, Sun.
    - Standard working hours: 09:00 - 17:00.
    - **Task Bundling**: Group tasks with the same 'location' (e.g. all 'Supermarket' errands) or 'tag' to minimize travel/context switching.
    - **Energy Flow**: Schedule 'High' priority tasks in morning slots (9-12) if possible.
    - **Locked Tasks**: If 'is_locked' is True and 'comments' specifies a time (e.g. "at 5pm"), you MUST respect that intent (e.g. start_time=17).
    - **Logic**: No overlaps. Respect duration.
    
    Output:
    - Return a JSON object matching the WeeklySchedule schema.
    - 'start_time' should be an integer hour (0-23).
    """

    # Single shot orchestration as per plan (no retry loop for now)
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
        print(f"Error during orchestration: {e}")
        # In a real app we might return an empty schedule or raise
        raise e
