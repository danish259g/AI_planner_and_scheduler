import os
import json
from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
from typing import Optional

from pathlib import Path

env_path = Path(__file__).parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except UnicodeDecodeError:
    # Fallback for UTF-16
    load_dotenv(dotenv_path=env_path, encoding='utf-16')

class Task(BaseModel):
    name: str = Field(description="The name or title of the task")
    duration: int = Field(description="Duration in minutes. Infer if not specified (default 30)")
    tag: str = Field(description="Category of the task (e.g., Work, Personal, Health, Errand)")
    location: str = Field(description="Location context (e.g., Home, Office, Gym, Supermarket)")
    priority: str = Field(description="Priority level: High, Medium, or Low")
    is_locked: bool = Field(description="True if the task has a specific time constraint (anchored), False otherwise")
    day: Optional[str] = Field(description="Specific day if mentioned (e.g. 'Monday', 'Tue'). Use 3-letter abbreviation (Mon, Tue, Wed...) if possible.")
    start_time: Optional[str] = Field(description="Specific start time if mentioned (e.g. '15:00', '3pm'). Format as HH:MM if possible.")
    end_time: Optional[str] = Field(description="Specific end time if mentioned. Format as HH:MM if possible.")
    comments: str = Field(description="Any extra useful information or context extracted from the user input")

async def interpret_task(text: str) -> Task:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are a semantic extraction agent. Extract task information from this input: "{text}".
    
    Guidelines:
    - **name**: Concise title.
    - **duration**: In minutes. Infer logically (e.g. "quick call" = 15, "workout" = 60) if not stated.
    - **tag**: Classify into a broad category like Work, Personal, Health, Study, Home, Errand.
    - **location**: Infer the physical context. Defaults to "Home" or "Office" based on task type if unclear.
    - **priority**: Infer based on urgency words ("urgent", "must", "important") or nature of task. Default to Medium.
    - **is_locked**: Set to True ONLY if the user specifies a specific time (e.g. "at 5pm", "in the morning") OR specific day.
    - **day**: Extract specific day if present (e.g. "on Monday" -> "Mon"). Use Mon, Tue, Wed, Thu, Fri, Sat, Sun.
    - **start_time/end_time**: Extract specific time constraints if present (e.g. "at 5pm" -> start_time="17:00"). Use 24h format HH:MM.
    - **comments**: Store ONLY extra context or nuances that do NOT fit into the fields above. Do NOT repeat the day or time here if they were successfully extracted to their own fields. If everything is covered, leave empty.
    """

    # Single shot execution (No retries)
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash-lite', 
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': Task
            }
        )
        
        if response.parsed:
           return response.parsed
        
        # Fallback for robust parsing
        data = json.loads(response.text)
        return Task(**data)

    except Exception as e:
        raise e
