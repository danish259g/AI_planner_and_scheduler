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
    task_id: Any = Field(description="The ID of the event being scheduled")
    day: str = Field(description="Day of the week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)")
    start_time: int = Field(description="Start hour (0-23)")
    duration_mins: int = Field(description="Duration in minutes")
    rationale: Optional[str] = Field(description="Brief reason for this slot (e.g. 'Bundled with other errands', 'High energy morning slot')")

class WeeklySchedule(BaseModel):
    thought_process: List[str] = Field(description="Step-by-step reasoning. FIRST, list the available time slots. SECOND, go through each event and assign it a slot, explicitly checking for overlaps. THIRD, summarize the final plan.")
    schedule: List[OrchestratedTask]
    logic_summary: str = Field(description="A brief (1-3 sentences) explanation of only the important remarks on how you solved the schedule, highlighting any compromises, bundles, or trade-offs made.")

async def orchestrate_schedule(events: List[Dict[str, Any]], user_profile: str = "", user_feedback: str = None) -> WeeklySchedule:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Convert events to a cleaner format for the LLM
    # We strip out implementation details and send the rich semantic fields
    clean_events = []
    for t in events:
        clean_events.append({
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

    task_list_str = json.dumps(clean_events, indent=2)

    
    # --- PROMPT ENGINEERING ---

    if user_feedback:
        # 1. ADJUSTMENT MODE
        # The goal is to modify the existing schedule based on feedback, minimizing disruption.
        prompt = f"""
        You are an Intelligent Schedule Adjuster.
        Your expertise is scheduling while using logical thinking and assigning events in times and order that makes sense, like an intelligent human would.
           - You don't just assign events to available times, but you also consider the context of the event and the user's profile.
           - you try and bundle similar events together to make the schedule more efficient.

        [CONTEXT]
        The user has an existing schedule. They have provided specific FEEDBACK to change it.
        
        [USER FEEDBACK]
        "{user_feedback}"
        
        [USER VIBE]
        "{user_profile}"

        [events & CURRENT STATE]
        {task_list_str}

        [INSTRUCTIONS]
        1. **Scratchpad Reasoning**: Use the 'thought_process' field to:
           - Identify the event/s to move.
           - Check the target slot for existing events.
           - If occupied, determine where to move the displaced event.
           - Verify no 2 events occupy the same hour.
        2. Minimal Disruption: ONLY change what is necessary.
        3. Resolve Conflicts: No overlaps allowed.

        [LAST STEP BEFORE YOUR OUTPUT DELIVERY]
        Review the schedule you've assigned, and make sure NO OVERLAPS exist. 
        If there are any, fix them according to above instructions.

        Output:
        - Return a JSON object matching the WeeklySchedule schema.
        - logic_summary: Explicitly state what changed.
        """
    else:
        # 2. GENERATION MODE
        # The goal is to build the optimal schedule from scratch.
        prompt = f"""
        You are an AI Scheduler. 
        Your goal is to build the BEST weekly schedule from scratch.
        Your expertise is scheduling while using logical thinking and assigning events in times and order that makes sense, like an intelligent human would.
           - You don't just assign events to available times, but you also consider the context of the event and the user's profile.
           - you try and bundle similar events together to make the schedule more efficient.

        [USER VIBE & PREFERENCES]
        "{user_profile}"

        [INPUT events]
        {task_list_str}

        [INSTRUCTIONS]
        1. Order of work:
           a. schedule the "locked" events to their defined timeframes
           b. examine remaining open frames, and assign the remaining events
        2. Scratchpad Reasoning (CRITICAL): 
           - In the 'thought_process' list, you MUST mentally simulate the week hour-by-hour.
           - For each event, write: "Attempting [event] at [Day] [Time]... Checking for overlap... [Result]"
           - If an overlap is found, retry with a new slot.
        3. Constraint Satisfaction: 
           - Respect 'is_locked' events exactly.
           - Fit all other events into valid slots (Sun-Sat, 8-22 hours).
           - NO OVERLAPS ALLOWED. Two events cannot interfere with each other (based on scheduled_start and scheduled_end).
        4. Completeness: Schedule EVERY event.

        [LAST STEP BEFORE YOUR OUTPUT DELIVERY]
        Review the schedule you've assigned, and make sure NO OVERLAPS exist. 
        If there are any, fix them according to above instructions.
        
        Output:
        - Return a JSON object matching the WeeklySchedule schema.
        """

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
