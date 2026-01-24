import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# --- Data Structures ---

class CognitiveType(Enum):
    ANALYTICAL = "Analytical"       # Math, Logic, Geometry - Needs Peak Fluid Intelligence
    CREATIVE = "Creative"           # Essay, Writing, Ideation - Needs Morning Clarity
    MEMORY = "Memory"               # Vocab, Formulas - Needs Glucose or Consolidation
    REVIEW = "Review"               # Error Logs, Review - Best for Consolidation (Pre-Sleep)
    GENERAL = "General"             # Reading, Etc.

@dataclass
class OptimizationTask:
    id: str
    name: str
    duration_mins: int
    subject: str            # 'Quantitative', 'Verbal', 'English', 'Essay'
    cognitive_type: CognitiveType
    priority: str           # 'High', 'Medium', 'Low'
    is_locked: bool = False
    fixed_start: Optional[float] = None # 0-24
    
@dataclass
class TimeSlot:
    start_hour: float    # e.g. 13.5 = 13:30
    end_hour: float      # e.g. 14.25 = 14:15
    task: Optional[OptimizationTask] = None

# --- Constants & Laws ---

ANALYTICAL_PEAK_START = 13.5  # 1:30 PM (Per User Rule)
ANALYTICAL_PEAK_END = 16.0    # Broadened slightly

MORNING_VERBAL_START = 8.0
MORNING_VERBAL_END = 11.5     # Until 11:30

GLUCOSE_SPIKE_LUNCH = 14.0    # Post Lunch
GLUCOSE_SPIKE_DINNER = 20.0   # Post Dinner
GLUCOSE_WINDOW = 1.0          # Duration of spike effect

MAX_CONSECUTIVE_MINUTES = 90  # The 90-Minute Law

class DailyBatchOptimizer:
    """
    Optimizes a SINGLE day's schedule using a Greedy approach with Scoring Heuristics.
    Strictly enforces: No Overlaps, Fixed Constraints.
    Softly enforces: Cognitive Laws (via scoring).
    """

    def __init__(self, day_name: str, constraints: List[Dict[str, Any]], user_settings: Dict[str, Any]):
        self.day_name = day_name
        self.constraints = constraints # List of {start: float, end: float, name: str}
        self.settings = user_settings
        
        self.day_start = float(user_settings.get('study_start', 8))
        self.day_end = float(user_settings.get('study_end', 22))
        self.peak_energy = user_settings.get('peak_energy', 'morning') # 'morning' or 'evening'
        
        # Grid of used time (Resolution: 15 mins = 0.25)
        # We'll just store placed tasks and check overlaps dynamically
        self.scheduled_tasks: List[TimeSlot] = []

    def solve(self, tasks: List[OptimizationTask]) -> List[Dict[str, Any]]:
        """
        Main entry point. Returns list of dicts with 'id', 'start_time', 'end_time'.
        """
        # 1. Place Locked Tasks First
        locked_tasks = [t for t in tasks if t.is_locked]
        flexible_tasks = [t for t in tasks if not t.is_locked]
        
        # Sort flexible tasks: High Priority & Longest Duration First
        # (Harder tasks are harder to fit, so place them early)
        flexible_tasks.sort(key=lambda t: (
            0 if t.priority == 'High' else 1 if t.priority == 'Medium' else 2,
            -t.duration_mins
        ))

        # Place Locked
        for t in locked_tasks:
            if t.fixed_start is None:
                continue # Should not happen for locked
            
            end_time = t.fixed_start + (t.duration_mins / 60.0)
            if self._is_slot_free(t.fixed_start, end_time):
                self.scheduled_tasks.append(TimeSlot(t.fixed_start, end_time, t))
            else:
                print(f"WARNING: Locked task {t.name} overlaps with constraints! Skipping.")

        # Place Flexible
        for t in flexible_tasks:
            best_score = -float('inf')
            best_start = -1.0
            
            # Search space: Start of day to End of day, step 15 mins
            current_time = self.day_start
            while current_time + (t.duration_mins/60.0) <= self.day_end:
                end_time = current_time + (t.duration_mins/60.0)
                
                if self._is_slot_free(current_time, end_time):
                    score = self._score_slot(t, current_time)
                    if score > best_score:
                        best_score = score
                        best_start = current_time
                
                current_time += 0.25 # 15 min step

            # If we found a valid slot, place it
            if best_start != -1.0:
                # [STRICT LIMIT CHECK]
                # Check if adding this task exceeds the daily limit
                # We do this check greedy-style: if it fits the schedule but breaks the limit, we skip it.
                # Ideally, we should have filtered before, but duration-based filtering is trickier with gaps.
                
                # Calculate total minutes scheduled so far
                total_mins = sum(s.task.duration_mins for s in self.scheduled_tasks)
                daily_limit_mins = self.settings.get('max_daily_hours', 4) * 60
                
                if total_mins + t.duration_mins > daily_limit_mins:
                    print(f"Optimization: Skipping task {t.name} ({t.duration_mins}m) - Daily limit reached ({total_mins}m used)")
                    continue

                self.scheduled_tasks.append(TimeSlot(best_start, best_start + (t.duration_mins/60.0), t))
                # Sort scheduled tasks by time to keep state clean
                self.scheduled_tasks.sort(key=lambda s: s.start_hour)
            else:
                print(f"Optimization: Could not fit task {t.name} ({t.duration_mins}m) on {self.day_name}")

        # Convert back to simple response format
        result = []
        for slot in self.scheduled_tasks:
            result.append({
                "id": slot.task.id,
                "day": self.day_name,
                "start_time": slot.start_hour,
                "end_time": slot.end_hour
            })
        return result

    def _is_slot_free(self, start: float, end: float) -> bool:
        # 1. Check User Constraints (Gym, Work) based on day
        # Constraints passed in are specific to this day
        for c in self.constraints:
            c_start = float(c['start'])
            c_end = float(c['end'])
            if max(start, c_start) < min(end, c_end): # Overlap formula
                return False

        # 2. Check already scheduled tasks
        for slot in self.scheduled_tasks:
            if max(start, slot.start_hour) < min(end, slot.end_hour):
                return False
        
        return True

    def _score_slot(self, task: OptimizationTask, start_time: float) -> float:
        score = 0.0
        
        # --- 1. The Analytical Peak Law (1:30 PM) ---
        # Highly analytical tasks (Quant) get a MASSIVE boost around 13:30
        if task.cognitive_type == CognitiveType.ANALYTICAL:
            # Distance from 13:30
            dist = abs(start_time - 13.5) 
            if dist < 1.0: score += 50  # Sweet spot
            elif dist < 2.0: score += 20
            else: score -= 10 # Penalty for doing math late at night or super early

        # --- 2. The Morning Verbal Law ---
        # Creative/Focus tasks prefer 08:00 - 11:00
        if task.cognitive_type == CognitiveType.CREATIVE:
            if MORNING_VERBAL_START <= start_time <= MORNING_VERBAL_END:
                score += 30
            elif start_time > 18.0: # Too late for heavy reading
                score -= 20

        # --- 3. The Verbal Glucose Law (Memory) ---
        # Memory/Vocab tasks prefer post-lunch (14:00) or post-dinner (20:00)
        # AND Consolidation (Before Sleep)
        if task.cognitive_type == CognitiveType.MEMORY:
            dist_lunch = abs(start_time - GLUCOSE_SPIKE_LUNCH)
            dist_dinner = abs(start_time - GLUCOSE_SPIKE_DINNER)
            dist_sleep = (self.day_end - start_time)
            
            if dist_lunch < 1.0 or dist_dinner < 1.0:
                score += 40 # Glucose Spike
            elif dist_sleep < 1.5:
                score += 30 # Consolidation Law (Before Sleep)
            else:
                score += 0 

        # --- 4. The Consolidation Law (Review) ---
        # Review tasks get boost if they are late in the day (last 2 hours)
        if task.cognitive_type == CognitiveType.REVIEW:
            if start_time >= (self.day_end - 2.0):
                score += 50
            elif start_time < 12.0:
                score -= 10 # Don't review in morning, learn new stuff

        # --- 5. The Interleaving Law & 90-Minute Law ---
        # Check the task IMMEDIATELY BEFORE this slot
        prev_slot = self._get_task_before(start_time)
        if prev_slot:
            # Interleaving: Bonus for switching subjects
            if prev_slot.task.subject != task.subject:
                score += 20
            else:
                score -= 10 # Slight penalty for monotony

            # 90-Minute Law: HARD PENALTY if extending a block too long
            # Calculate how long we've been doing this subject
            consecutive_mins = self._calc_consecutive_subject_minutes(prev_slot, task.subject)
            if consecutive_mins + task.duration_mins > MAX_CONSECUTIVE_MINUTES:
                score -= 1000 # BLOCK THIS SLOT

        # --- 6. User Preference: Morning Person vs Evening ---
        # --- 6. User Preference: Morning Person vs Evening ---
        import math
        
        if self.peak_energy == 'morning':
            if start_time < 12: score += 50
            elif start_time > 18: score -= 30
            
        elif self.peak_energy == 'evening':
            if start_time > 16: score += 50
            elif start_time < 12: score -= 30
            
        elif self.peak_energy == 'afternoon':
             if 12 <= start_time <= 17: score += 50
             elif start_time < 10 or start_time > 20: score -= 20

        # --- 7. The Cool Down Law (Post-Class Buffer) ---
        # If there is a constrained event (class) recently, we need a break.
        prev_constraint = self._get_constraint_before(start_time)
        if prev_constraint:
            # If immediately after (gap < 45m), BIG penalty for heavy cognitive work
            gap = start_time - float(prev_constraint['end'])
            if gap < 0.75: # Less than 45 mins
                 if task.cognitive_type in [CognitiveType.ANALYTICAL, CognitiveType.CREATIVE]:
                     score -= 40 # Force a break or lighter task
                 else:
                     score -= 10 # still prefer a customized break

        return score

    def _get_constraint_before(self, start_time: float) -> Optional[Dict]:
        """Find the nearest constraint that ends before or at start_time"""
        last_c = None
        closest_end = -1
        for c in self.constraints:
             end = float(c['end'])
             if end <= start_time:
                 if end > closest_end:
                     closest_end = end
                     last_c = c
        return last_c

    def _get_task_before(self, start_time: float) -> Optional[TimeSlot]:
        """Returns the task that ends exactly at or remarkably close to start_time"""
        # We assume tasks are sorted by start_time in self.scheduled_tasks
        # Scan backward
        for i in range(len(self.scheduled_tasks)-1, -1, -1):
            slot = self.scheduled_tasks[i]
            if abs(slot.end_hour - start_time) < 0.25: # Within 15 mins gap
                return slot
            if slot.end_hour < start_time: # Optimization: stops if we go too far back
                return None
        return None

    def _calc_consecutive_subject_minutes(self, last_slot: TimeSlot, subject: str) -> int:
        """Backtrack to see how long we've been doing this subject"""
        total_mins = last_slot.task.duration_mins
        
        # This is a bit recursive or iterative backtracking
        # For simplicity in this greedy approach, we just look at the immediate neighbor chain
        # Ideally we'd look at the whole chain. Let's try to look back one more step.
        
        # Simplification: We only care about the immediate block. 
        # Truly enforcing 90m requires looking back recursively.
        # Let's do a quick scan of the calculated schedule list.
        
        # Find index of last_slot
        idx = -1
        try:
           idx = self.scheduled_tasks.index(last_slot)
        except ValueError:
            return 0
            
        current_idx = idx
        while current_idx >= 0:
             curr = self.scheduled_tasks[current_idx]
             
             # Check continuity (gap < 15 mins)
             if current_idx > 0:
                 prev = self.scheduled_tasks[current_idx-1]
                 if curr.start_hour - prev.end_hour > 0.25:
                     break # Break in chain
             
             # Check subject
             if current_idx > 0: # Check previous
                 prev = self.scheduled_tasks[current_idx-1]
                 if prev.task.subject == subject:
                     total_mins += prev.task.duration_mins
                     current_idx -= 1
                 else:
                     break
             else:
                 break
                 
        return total_mins
