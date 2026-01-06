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
        prompt = f"""
        You are an **Expert Psychometric Tutor & Schedule Optimizer**.
        The user has provided feedback to adjust their study plan.

        [USER FEEDBACK]
        "{user_feedback}"
        
        [USER PROFILE/NOTES]
        "{user_profile}"

        [CURRENT TASK LIST & SCHEDULE]
        {task_list_str}

        [GOAL]
        Modify the schedule to address the feedback while maintaining a high-quality study structure.

        [HARD CONSTRAINTS - VIOLATION = FAILURE]
        1. **Locked Tasks**: Respect 'is_locked=True' tasks (keep day/time unless user explicitly asks to move them).
        2. **No Overlaps**: Two tasks cannot occupy the same time slot.
        3. **Valid Hours**: Schedule strictly between 08:00 and 23:00 unless a Locked task forces otherwise.

        [HEURISTIC GUIDELINES - OPTIMIZE FOR THESE]
        1. **Study Diversity (The 3-Hour Rule)**: Avoid scheduling the SAME Subject (Quantitative/Verbal/English) for more than 3 consecutive hours. Mix it up to keep the brain fresh.
        2. **Peak Performance**: Place "Simulations" (duration > 180m) in the morning (start 08:00-10:00) if possible.
        3. **Weakness Priority**: Treat 'High' priority tasks as must-haves for prime hours.
        4. **Minimal Disruption**: When adjusting, try to keep other unrelated tasks stable.

        [OUTPUT INSTRUCTIONS]
        - Return a JSON object matching the WeeklySchedule schema.
        - **thought_process**: Explain which constraints you checked and how you optimized.
        - **logic_summary**: Briefly tell the student what you changed and why.
        """
    else:
        # 2. GENERATION MODE
        prompt = f"""
        You are an **Expert Psychometric Tutor & Schedule Optimizer**.
        Your goal is to build the OPTIMAL study plan for the week from these tasks.

        [USER PROFILE/NOTES]
        "{user_profile}"

        [TASK LIST]
        {task_list_str}

        [HARD CONSTRAINTS - VIOLATION = FAILURE]
        1. **Locked Tasks**: You MUST place 'is_locked=True' tasks at their specific 'day' and 'start_time'. Do this FIRST.
        2. **No Overlaps**: No two tasks can overlap in time.
        3. **Valid Hours**: Tasks must be scheduled between 08:00 and 23:00.

        [HEURISTIC GUIDELINES - OPTIMIZE FOR THESE]
        1. **Subject Mixing (The 3-Hour Rule)**: Do not schedule > 3 hours of the *same* Subject (Quantitative, Verbal, English) consecutively. Alternate subjects to maximize retention.
        2. **Simulation Blocks**: If a task is a "Simulation" (duration > 180m), prioritize placing it in the morning (e.g., starting 08:00 or 09:00) on a day with few other commitments.
        3. **Vocab Spacing**: If there are multiple short "English" or "Vocab" tasks, spread them out across different days rather than bunching them.
        4. **Weakness First**: Schedule 'High' priority tasks earlier in the day or week.

        [STEP-BY-STEP REASONING "thought_process"]
        1. **Anchor Locked**: "Placing locked task X at [Day] [Time]".
        2. **Place Simulations**: "Found Simulation task X. Looking for a morning slot..."
        3. **Fill Gaps**: "Iterating through remaining tasks... Attempting to place [Task Y] (Math) after [Task Z] (English) to mix subjects."
        4. **Review**: "Checking for overlaps... All clear."

        [OUTPUT]
        - Return a JSON object matching the WeeklySchedule schema.
        - Ensure every single task from the input is assigned a valid 'day' and 'start_time'.
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
