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
    - **is_locked**: Set to True ONLY if the user specifies a specific time (e.g. "at 5pm", "in the morning"). NOTE: You are extracting *intent*, not scheduling. If they say "at 5pm", mark is_locked=True.
    - **comments**: Store any original time constraints (e.g. "at 5pm") or nuances here.
    """

    # Retry logic handles 429
    max_retries = 1
    base_delay = 10

    for attempt in range(max_retries):
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
             # Check for 429/ResourceExhausted
            if "429" in str(e) or "ResourceExhausted" in str(e) or "quota" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
            raise e
