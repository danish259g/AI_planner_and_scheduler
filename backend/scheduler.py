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

from backend.optimizer import DailyBatchOptimizer, OptimizationTask, CognitiveType

env_path = Path(__file__).parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except UnicodeDecodeError:
    load_dotenv(dotenv_path=env_path, encoding='utf-16')

# --- Models ---

class OrchestratedTask(BaseModel):
    task_id: Any = Field(description="The ID of the event being scheduled")
    day: str = Field(description="Day of the week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)")
    start_time: float = Field(description="Start hour (0-23). Use decimals for minutes, e.g., 14.5 = 14:30")
    duration_mins: int = Field(description="Duration in minutes")
    rationale: Optional[str] = Field(description="Brief reason for this slot")

class WeeklySchedule(BaseModel):
    thought_process: List[str] = Field(description="Reasoning steps")
    schedule: List[OrchestratedTask]
    logic_summary: str = Field(description="Explanation of the schedule logic")
    task_profiles: Dict[str, str] = Field(default={}, description="Map of Task ID to Cognitive Type")

class TaskProfile(BaseModel):
    task_id: str
    cognitive_type: str = Field(description="Analytical, Creative, Memory, Review, or General")
    reasoning: str

class TaskProfileList(BaseModel):
    profiles: List[TaskProfile]

class DayAssignment(BaseModel):
    task_id: str
    day: str = Field(description="Mon, Tue, Wed, Thu, Fri, Sat, Sun")

class WeekStrategy(BaseModel):
    assignments: List[DayAssignment]
    strategy_reasoning: str

# --- Main Orchestrator ---

async def orchestrate_schedule(
    events: List[Dict[str, Any]], 
    user_profile: str = "", 
    user_feedback: str = None, 
    performance_data: Dict[str, Any] = None, 
    user_settings: Dict[str, Any] = None,
    profile_update_callback: Optional[Any] = None # Async callback(profile_map)
) -> WeeklySchedule:
    # 0a. [PERFORMANCE BOOST]: Automatically boost priority for weak subjects
    if performance_data:
        for task in events:
            tag = task.get("tag")
            if tag and tag in performance_data:
                # Store original priority just in case
                # task["original_priority"] = task.get("priority")
                
                perf = performance_data[tag]
                # If score is known (count > 0) and low (< 70)
                if perf.get("count", 0) > 0 and perf.get("score", 0) < 70:
                    print(f"Scheduler: Priority Boost for {task.get('name')} (Score: {perf.get('score')})")
                    task["priority"] = "High"

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found")
    
    client = genai.Client(api_key=api_key)
    
    try:
        # 0. Pre-processing: Map tasks for lookup
        task_map = {str(t["id"]): t for t in events}

        # Step 1: Profiling
        # Step 1: Profiling
        print("Scheduler: Step 1 - Profiling Tasks...")
        
        # Split tasks into those needing profile and those having it
        unknown_tasks = []
        profile_map = {}
        
        for t in events:
            tid = str(t["id"])
            if t.get("cognitive_type"):
                profile_map[tid] = t["cognitive_type"]
            else:
                unknown_tasks.append(t)
        
        if unknown_tasks:
             print(f"Profiling {len(unknown_tasks)} new tasks...")
             new_profiles = await _get_cognitive_profiles(client, unknown_tasks)
             for p in new_profiles.profiles:
                 profile_map[p.task_id] = p.cognitive_type
             
             # IMMEDIATE SAVE CALLBACK
             if profile_update_callback:
                 print("Scheduler: Triggering immediate profile save...")
                 try:
                     await profile_update_callback(profile_map)
                 except Exception as e:
                     print(f"Warning: Profile save callback failed: {e}")

        else:
             print("Skipping Profiling (All tasks known)")
             
        # Mock profile object for passing to strategist if needed, or just construct list
        # We need a TaskProfileList object for Step 2 if we want to keep signature same
        # Reconstruct list from map
        all_profiles_list = [TaskProfile(task_id=tid, cognitive_type=ctype, reasoning="Loaded/Cached") for tid, ctype in profile_map.items()]
        profiles = TaskProfileList(profiles=all_profiles_list)
        
        # Step 2: Strategizing Week
        print("Scheduler: Step 2 - Strategizing Week...")
        strategy = await _generate_week_strategy(client, events, profiles, user_settings, user_profile, user_feedback)
        
        print(f"DEBUG: Strategist Reason: {strategy.strategy_reasoning}")
        print(f"DEBUG: Strategist assigned {len(strategy.assignments)} tasks.")
        if len(strategy.assignments) == 0:
             print("DEBUG: ALERT! Strategist assigned ZERO tasks. Check prompt or capacity.")
        
        # Step 3: Tactical Optimization
        print("Scheduler: Step 3 - Optimizing Days (The Tactician)...")
        
        final_schedule = []
        tasks_by_day = {d: [] for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]}
        
        for assignment in strategy.assignments:
            tid = assignment.task_id
            
            # Simple ID usage
            if tid not in task_map: 
                 # Tolerance for string/int mismatch
                 print(f"Warning: Strategist ID {tid} not in map")
                 continue
            
            raw = task_map[tid]
            
            # ... (Rest of logic uses raw dict using short_id lookup)
            
            # Create OptimizationTask
            # Map string cognitive type to Enum
            c_type_str = profile_map.get(tid, "General")
            try:
                c_type = CognitiveType(c_type_str)
            except:
                c_type = CognitiveType.GENERAL
            
            opt_task = OptimizationTask(
                id=tid,
                name=raw.get("name", "Unknown"),
                duration_mins=raw.get("duration", 30),
                subject=raw.get("tag", "General"), # Using tag as subject
                cognitive_type=c_type,
                priority=raw.get("priority", "Medium"),
                is_locked=raw.get("is_locked", False),
                fixed_start=raw.get("start_time") if raw.get("is_locked") else None
            )
            
            # If task is locked, FORCE it to its locked day, ignoring Strategist
            if opt_task.is_locked and raw.get("day"):
                 # Override strategist
                 tasks_by_day[raw["day"]].append(opt_task)
            elif assignment.day in tasks_by_day:
                 tasks_by_day[assignment.day].append(opt_task)
        
        # 3b. Run Optimizer for each Day
        full_timeline = []
        
        for day, day_tasks in tasks_by_day.items():
            if not day_tasks: continue
            
            # Filter constraints for this day
            daily_constraints = [
                c for c in user_settings.get('constraints', []) 
                if c.get('day') == day
            ]
            
            optimizer = DailyBatchOptimizer(day, daily_constraints, user_settings)
            results = optimizer.solve(day_tasks)
            
            for res in results:
                full_timeline.append(OrchestratedTask(
                    task_id=res["id"],
                    day=res["day"],
                    start_time=res["start_time"],
                    duration_mins=int((res["end_time"] - res["start_time"]) * 60),
                    rationale=f"Optimized for {profile_map.get(str(res['id']), 'General')} performance"
                ))

        # Step 4: Explanation (The Narrator)
        # Explains the final Result
        print("Scheduler: Step 4 - Examining Result...")
        # summary = await _explain_schedule(client, full_timeline, strategy.strategy_reasoning) 
        # Using simple summary for speed for now, or minimal prompt
        
        return WeeklySchedule(
            thought_process=[
                f"Configured {len(profiles.profiles)} task profiles.",
                f"Strategist Balanced Week: {strategy.strategy_reasoning}",
                f"Tactician Optimized {len(full_timeline)} slots using Cognitive Laws."
            ],
            schedule=full_timeline,
            logic_summary=strategy.strategy_reasoning,
            task_profiles=profile_map
        )
        
    except Exception as e:
        # Fallback logging
        error_log_path = Path(__file__).parent / 'scheduler_error.log'
        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.datetime.now()}] ERROR in orchestrate_v2:\n")
            f.write(traceback.format_exc())
        print(f"Scheduler Error: {e}")
        raise e

# --- Helper Prompts ---

async def _get_cognitive_profiles(client, events):
    # Simplified list for prompt
    simple_events = [{k: v for k, v in t.items() if k in ['id', 'name', 'tag']} for t in events]
    
    prompt = f"""
    Analyze the cognitive load of these study tasks.
    Assign each a 'cognitive_type' from:
    1. 'Analytical' (Math, Geometry, Logic, Data Analysis) - Requires heavy fluid intelligence.
    2. 'Creative' (Essay, Writing, Brainstorming) - Requires focus and verbal fluency.
    3. 'Memory' (Vocabulary, Flashcards, Formulas) - Rote memorization.
    4. 'Review' (Error Logs, Debriefing) - Looking at past work.
    5. 'General' (Reading, Admin, Misc) - Low specific load.

    Tasks: {json.dumps(simple_events)}
    """
    
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt,
        config={'response_mime_type': 'application/json', 'response_schema': TaskProfileList}
    )
    return response.parsed


async def _generate_week_strategy(client, events, profiles, user_settings, user_profile, feedback):
    # Dynamic Prompt Construction based on Style
    style = user_settings.get('scheduling_style', 'spread')
    
    # Calculate Theoretical Min Days
    total_duration_mins = sum([t.get('duration', 30) for t in events])
    max_daily_hours = user_settings.get('max_daily_hours', 4)
    if max_daily_hours <= 0: max_daily_hours = 4
    
    min_days_needed = (total_duration_mins / 60.0) / max_daily_hours
    import math
    target_days = math.ceil(min_days_needed)
    
    if style == 'batch':
        style_goals = f"""
    2. **Batching**: 
       - **TARGET ACTIVE DAYS**: {target_days} (or max {target_days + 1}).
       - Total Work is {total_duration_mins} mins. Max/Day is {max_daily_hours*60} mins.
       - You MUST fit everything into approximately {target_days} days.
       - LEAVE THE OTHER {7 - target_days} DAYS EMPTY.
       - decide on which days are best to fill 
        """
        energy_instruction = """
    [ENERGY - BATCH MODE]
    - Treat days as buckets of capacity.
    - If a day (e.g. Thu) has a class, only use it if Mon-Wed are FULL or if you absolutely need the spillover.
    - **DO NOT** drop tasks. Open a new Day bin if current one is full.
        """
    else:
        # Spread Mode (Default)
        style_goals = """
    2. **Balance**: Distribute total duration evenly across all available days.
    3. **Spread Consistently**: Ensure no single day is significantly heavier than others (unless needed for High Priority).
    4. **Strategy**: Tasks marked 'High' Priority MUST be assigned to optimal days.
        """
        energy_instruction = """
    [ENERGY - SPREAD MODE]
    1. Calculate "Free Capacity" = (Max Daily Hours) - (Fixed Constraints).
    2. **DO NOT** overload days with classes. If a day has a long event (>4h), assign VERY FEW tasks to it to prevent burnout.
        """

    prompt = f"""
    You are the Strategic Planner. Assign each task to a DAY of the week (Sun-Sat).
    
    [USER PROFILE]: {user_profile}
    [FEEDBACK]: {feedback if feedback else "None"}
    [CONSTRAINTS]: {json.dumps(user_settings.get('constraints', []))}
    [MAX DAILY HOURS]: {user_settings.get('max_daily_hours', 4)}
    [SCHEDULING STYLE]: {style}
    
    {energy_instruction}

    [CRITICAL PRIORITY]
    **DO NOT DROP TASKS** unless the *entire week's* capacity is reached. 

    [GOALS]
    1. **Interleaving**: Mix subjects (Quant/Verbal/English) on the same day.
    {style_goals}
    
    [TASKS With Profiles]:
    {json.dumps([t for t in events], default=str)}
    
    [Cognitive Tags]:
    {json.dumps([p.dict() for p in profiles.profiles])}

    Output a valid JSON with 'assignments' (task_id, day) and 'strategy_reasoning'.
    """
    

    
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt,
        config={'response_mime_type': 'application/json', 'response_schema': WeekStrategy}
    )
    return response.parsed
