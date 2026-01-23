import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from google import genai
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from pathlib import Path
import traceback
import datetime

env_path = Path(__file__).parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except UnicodeDecodeError:
    load_dotenv(dotenv_path=env_path, encoding='utf-16')

class OrchestratedTask(BaseModel):
    task_id: Any = Field(description="The ID of the event being scheduled")
    day: str = Field(description="Day of the week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)")
    start_time: float = Field(description="Start hour (0-23). Use decimals for minutes, e.g., 14.5 = 14:30")
    duration_mins: int = Field(description="Duration in minutes")
    rationale: Optional[str] = Field(description="Brief reason for this slot (e.g. 'Bundled with other errands', 'High energy morning slot')")

    @validator('start_time', pre=True)
    def parse_start_time(cls, v):
        if isinstance(v, str):
            # Handle "09:30" format
            if ':' in v:
                try:
                    h, m = map(float, v.split(':'))
                    return h + (m / 60)
                except ValueError:
                    pass
            # Handle "9" or "9.5" string
            try:
                return float(v)
            except ValueError:
                pass
        return v

class WeeklySchedule(BaseModel):
    thought_process: List[str] = Field(description="CONCISE, bullet-point reasoning for the schedule. Do NOT explain every step. Only mention key trade-offs or constraints handled.")
    schedule: List[OrchestratedTask]
    logic_summary: str = Field(description="A brief (1-3 sentences) explanation of only the important remarks on how you solved the schedule, highlighting any compromises, bundles, or trade-offs made.")

async def orchestrate_schedule(events: List[Dict[str, Any]], user_profile: str = "", user_feedback: str = None, performance_data: Dict[str, Any] = None, user_settings: Dict[str, Any] = None) -> WeeklySchedule:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    perf_str = json.dumps(performance_data, indent=2) if performance_data else "No data yet."

    # Convert events to a cleaner format for the LLM
    # We strip out implementation details and send the rich semantic fields
    clean_events = []
    for t in events:
        clean_events.append({
            "id": str(t["id"]),
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

        [STUDENT PERFORMANCE DATA]
        {perf_str}

        [GOAL]
        Modify the schedule to address the feedback while maintaining a high-quality study structure.

        [HARD CONSTRAINTS - VIOLATION = FAILURE]
        1. **Locked Tasks**: Respect 'is_locked=True' tasks (keep day/time unless user explicitly asks to move them).
        2. **STRICTLY NO OVERLAPS**: Two tasks cannot occupy the same time slot. If Task A is 10:00-11:00, Task B CANNOT start before 11:00.
        3. **Valid Hours**: Schedule strictly between 08:00 and 23:00 unless a Locked task forces otherwise.
        4. **Daily Capacity**: The total duration of study tasks assigned to any single day MUST NOT exceed {user_settings.get('max_daily_hours', 8)} hours.

        [OVERFLOW PROTOCOL]
        If you cannot fit all tasks without overlapping OR exceeding {user_settings.get('max_daily_hours', 8)} hours/day:
        1. **DROP** lower priority tasks.
        2. **DROP** tasks where the student's performance is already strong (High score).
        3. **KEEP** tasks that address weaknesses or have 'High' priority.
        4. Do NOT forcing tasks into the schedule if they don't fit. Omit them from the output.

        [HEURISTIC GUIDELINES - OPTIMIZE FOR THESE]
        1. **Peak Performance**: Respect Peak Energy Time: {user_settings.get('peak_energy', 'morning')}. Place intense tasks during this window if possible.
        2. **Scheduling Style**: Respect {user_settings.get('scheduling_style', 'spread')} style. (Spread = even distribution, Batch = group subjects together).
        3. **Study Diversity (The 3-Hour Rule)**: Avoid scheduling the SAME Subject (Quantitative/Verbal/English) for more than 3 consecutive hours. Mix it up to keep the brain fresh.
        4. **Weakness Priority**: Treat 'High' priority tasks as must-haves for prime hours.
        5. **Minimal Disruption**: When adjusting, try to keep other unrelated tasks stable.

        [OUTPUT INSTRUCTIONS]
        - Return a JSON object matching the WeeklySchedule schema.
        - **thought_process**: Keep it extremely concise (3-5 bullet points max).
        - **logic_summary**: Briefly tell the student what you changed and why.
        """
    else:
        # 2. GENERATION MODE
        prompt = f"""
        You are an **Expert Psychometric Tutor & Schedule Optimizer**.
        Your goal is to build the OPTIMAL study plan for the week from these tasks.

        [USER PROFILE/NOTES]
        "{user_profile}"

        [USER SETTINGS & CONSTRAINTS]
        Username/Profile: {user_settings.get('username', 'Student')}
        Study Window: {user_settings.get('study_start', 8)}:00 to {user_settings.get('study_end', 22)}:00
        Max Daily Study Hours: {user_settings.get('max_daily_hours', 8)} hours (DO NOT EXCEED THIS PER DAY)
        Peak Energy Time: {user_settings.get('peak_energy', 'morning')} (Schedule intense tasks here)
        Scheduling Style: {user_settings.get('scheduling_style', 'spread')} (Prefer this way of organizing tasks)
        Target Score Goal: {user_settings.get('target_score', 'High')}
        Fixed Outside Commitments (DO NOT SCHEDULE TASKS DURING THESE TIMES):
        {json.dumps(user_settings.get('constraints', []), indent=2)}

        [TASK LIST]
        {task_list_str}

        [STUDENT PERFORMANCE DATA]
        {perf_str}

        [HARD CONSTRAINTS - VIOLATION = FAILURE]
        1. **Locked Tasks**: You MUST place 'is_locked=True' tasks at their specific 'day' and 'start_time'. Do this FIRST.
        2. **Fixed Constraints**: DO NOT schedule any study tasks during the student's Fixed Outside Commitments (Work, gym, etc.). Treat these slots as "Blocked".
        3. **Study Window**: All tasks MUST be scheduled between {user_settings.get('study_start', 8)}:00 and {user_settings.get('study_end', 22)}:00.
        4. **ABSOLUTELY NO OVERLAPS**: If Task A is 09:00-10:00, Task B CANNOT start before 10:00. Overlaps are strictly forbidden.
        5. **3-Letter Days**: Use ONLY the 3-letter abbreviations for days: Sun, Mon, Tue, Wed, Thu, Fri, Sat. (NEVER use full names like "Tuesday").
        6. **STRICT Daily Capacity**: The total duration of study tasks assigned to any single day MUST NOT exceed {user_settings.get('max_daily_hours', 8)} hours. This is a HARD LIMIT.

        [HEURISTIC GUIDELINES - OPTIMIZE FOR THESE]
        0. **Weakness Focus**: prioritize categories with low 'score' or low 'self_eval' from the PERFORMANCE DATA. Give them prime slots and more frequent sessions.
        1. **Peak Energy Sync**: Use the student's energy window ({user_settings.get('peak_energy', 'morning')}) for the most difficult or high-priority tasks.
        2. **Scheduling Preference**: If style is 'batch', group similar subjects together on the same day. If 'spread', distribute different subjects across the week. Style requested: {user_settings.get('scheduling_style', 'spread')}.
        3. **Subject Mixing (The 3-Hour Rule)**: Do not schedule > 3 hours of the *same* Subject (Quantitative, Verbal, English) consecutively. Alternate subjects to maximize retention.
        4. **Simulation Blocks**: If a task is a "Simulation" (duration > 180m), prioritize placing it in the morning (e.g., starting 08:00 or 09:00) on a day with few other commitments.
        5. **Vocab Spacing**: If there are multiple short "English" or "Vocab" tasks, spread them out across different days rather than bunching them.
        6. **Weakness First**: Schedule 'High' priority tasks earlier in the day or week.

        [OVERFLOW PROTOCOL (CRITICAL)]
        If the total duration of tasks > available study hours OR daily limits are reached:
        1. You MUST **omit** tasks from the output rather than exceeding limits.
        2. **Prioritize Exclusion**: Drop tasks with 'Low' priority first, then tasks where the student has high performance scores.
        3. **Must Schedule**: Keep 'High' priority tasks and 'Simulation' blocks if possible.
        4. It is better to return a partial, valid schedule than a full schedule with overlaps.

        [CONCISE REASONING "thought_process"]
        1. **Locked**: Identified locked tasks.
        2. **Placement**: Placed high priority/weakness tasks in optimal slots.
        3. **Checks**: Verified 0 overlaps and Daily Limits.

        [OUTPUT]
        - Return a JSON object matching the WeeklySchedule schema.
        - **IMPORTANT**: If your tasks exceed the daily capacity for the entire week, prioritize scheduling the most important tasks and leave the lower-priority ones out of the 'schedule' array. 
        - Use ONLY 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' for the 'day' field.
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
        
        try:
            # print(f"DEBUG: Raw Gemini Response: {response.text}")
            text = response.text.strip()
            # Remove markdown fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[-1]
                if text.endswith("```"):
                    text = text.rsplit("\n", 1)[0]
                # Handle cases where the first line was ```json
                if text.startswith("json"):
                    text = text[4:].strip()
            
            data = json.loads(text)
            return WeeklySchedule(**data)
        except json.JSONDecodeError as e:
            # Log to file explicitly here
            error_log_path = Path(__file__).parent / 'scheduler_error.log'
            with open(error_log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.datetime.now()}] JSON DECODE ERROR:\n")
                f.write(f"Raw Text: {response.text}\n")
                f.write(f"Error: {e}\n")
            
            print(f"CRITICAL: Failed to decode JSON from Gemini: {response.text}")
            raise ValueError("Invalid JSON from Gemini")

    except Exception as e:
        # Log full traceback to file for debugging
        error_log_path = Path(__file__).parent / 'scheduler_error.log'
        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.datetime.now()}] ERROR in orchestrate_schedule:\n")
            f.write(traceback.format_exc())
            f.write("\n------------------------------------------------\n")

        error_msg = str(e).lower()
        if "503" in error_msg or "overloaded" in error_msg or "resource exhausted" in error_msg or "429" in error_msg:
            print(f"Gemini API Quota/Overload: {e}")
            raise ValueError("GEMINI_OVERLOADED")
        
        print(f"Error during orchestration: {e}")
        raise e
