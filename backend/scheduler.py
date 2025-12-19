import os
import json
import asyncio
from typing import List, Dict, Any
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except UnicodeDecodeError:
    load_dotenv(dotenv_path=env_path, encoding='utf-16')

class OrchestratedTask(BaseModel):
    task_id: Any
    day: str
    start_time: int
    duration_mins: int

class WeeklySchedule(BaseModel):
    schedule: List[OrchestratedTask]

async def orchestrate_schedule(tasks: List[Dict[str, Any]]) -> WeeklySchedule:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Convert tasks to a cleaner format for the LLM
    task_list_str = json.dumps([{
        "id": t.get("id"),
        "title": t.get("title"),
        "duration_mins": t.get("duration_mins", 60),
        "tag": t.get("tag", "General")
    } for t in tasks], indent=2)

    prompt = f"""
    You are an intelligent weekly scheduler. Your goal is to assign the following tasks to efficient time slots in a weekly calendar.
    
    Constraints:
    - The week days are: Mon, Tue, Wed, Thu, Fri, Sat, Sun.
    - Standard working hours are roughly 8:00 (8) to 18:00 (18), but you can schedule personal tasks outside these hours if appropriate.
    - Do not overlap tasks.
    - Respect the duration of each task.
    - Group similar tasks (by tag) together if possible to minimize context switching.
    - Output a valid JSON object matching the WeeklySchedule schema.
    - 'start_time' should be an integer hour (0-23). For simpler visualization, stick to full hours (e.g. 9, 14).

    Task List:
    {task_list_str}
    """

    max_retries = 2
    base_delay = 5

    for attempt in range(max_retries):
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
            if "429" in str(e) or "ResourceExhausted" in str(e) or "quota" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
            print(f"Error during orchestration: {e}")
            raise e
