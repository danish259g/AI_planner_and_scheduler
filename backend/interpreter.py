import os
import json
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

try:
    load_dotenv()
except UnicodeDecodeError:
    # Fallback for UTF-16
    load_dotenv(encoding='utf-16')

class Task(BaseModel):
    task_name: str
    duration: int

async def interpret_task(text: str) -> Task:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are a semantic extraction agent. Extract task information from this input: "{text}".
    Infer reasonable duration in minutes if not stated.
    """

    # Retry logic handles 429
    max_retries = 1
    base_delay = 10

    for attempt in range(max_retries):
        try:
            # New SDK allows passing the Pydantic model directly into response_schema
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash-lite', 
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': Task
                }
            )
            
            # response.parsed is available when response_schema is provided
            # However, for Pydantic models with google-genai, it returns a dict or the model instance depending on version.
            # Safe bet: parse the text if parsed isn't exactly what we expect, or rely on .parsed if documented.
            # The new SDK `parsed` property usually returns the Pydantic object if class is passed.
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
