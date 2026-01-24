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

from backend.task_catalog import TASK_CATALOG

async def interpret_task(text: str) -> Task:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Format catalog for prompt
    catalog_str = json.dumps(TASK_CATALOG, indent=2)

    prompt = f"""
    You are a specialized Semantic Extractor for a Psychometric Test Study Planner. 
    Your job is to extract study task information from the user input: "{text}".

    [STRICT DOMAIN ENFORCEMENT]
    - This system ONLY handles study tasks for the Psychometric Entrance Test.
    - If the user input is clearly NOT study-related, tag as 'Personal'/'Errand' with 'Low' priority.

    [TASK CATALOG - BASE NAMES]
    The user's intent must map to one of these BASE names, but you strict formatting rules apply:
    {list(TASK_CATALOG.keys())}

    [NAMING CONVENTIONS - STRICT]
    1. **Progressive Tasks** (Geometry, Algebra, etc.):
       - If a number/chapter is mentioned, APPEND it. 
       - Format: "{{Base Name}} {{Number}}" (e.g., "Geometry 1", "Algebra 5").
    2. **Vocabulary**:
       - ALWAYS Prepend language (ENG/HEB) if detectable (Default to ENG).
       - APPEND unit number if mentioned.
       - Format: "{{Lang}} Vocabulary {{Number}}" (e.g., "ENG Vocabulary 1", "HEB Vocabulary 2").
    3. **Standard Tasks** (Essay, Simulation):
       - Use the Base Name exactly (e.g., "Essay Writing").

    [FIELDS TO EXTRACT]
    - **name**: The formatted name following conventions above.
    - **duration**: In minutes. Use defaults unless user specifies otherwise.
    - **tag**: Use the tag associated with the chosen BASE name.
    - **location**: Any remaining details (e.g., "Triangles", "Review").
    - **priority**: 'High' if urgent/weakness, else 'Medium'.
    - **is_locked**: True ONLY if specific time is mandated.
    - **day/start_time/end_time**: As specified.
    - **comments**: Original context.
    
    [INFERENCE RULES]
    - Input: "Do geometry chapter 1" -> name="Geometry 1", tag="Quantitative"
    - Input: "Learn english words unit 5" -> name="ENG Vocabulary 5", tag="English"
    - Input: "Hebrew analogies" -> name="HEB Analogies", tag="Verbal" (Verify 'Analogies' is in catalog)
    - Input: "Essay" -> name="Essay Writing"
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
