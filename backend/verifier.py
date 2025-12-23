from typing import List, Dict, Any
from .scheduler import OrchestratedTask, WeeklySchedule

def verify_schedule_algorithmic(schedule_data: WeeklySchedule) -> List[str]:
    """
    Checks for hard constraints:
    1. Overlaps between tasks.
    2. Start/End times within valid 0-23 range.
    Returns a list of error messages. Empty list means valid.
    """
    errors = []
    tasks = schedule_data.schedule
    
    # Sort by day and start time
    week_order = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
    sorted_tasks = sorted(tasks, key=lambda t: (week_order.get(t.day, 99), t.start_time))

    # Check for overlaps
    for i in range(len(sorted_tasks)):
        t1 = sorted_tasks[i]
        
        # Range check
        if not (7 <= t1.start_time <= 23):
             errors.append(f"Task {t1.task_id} has invalid start time: {t1.start_time}")
        
        # End time check (approximate, since we only have duration in mins)
        end_time_hour = t1.start_time + (t1.duration_mins / 60)
        if end_time_hour > 24:
             errors.append(f"Task {t1.task_id} goes beyond midnight.")

        # Overlap check
        for j in range(i + 1, len(sorted_tasks)):
            t2 = sorted_tasks[j]
            
            # Different day, no overlap possible (since list is sorted by day)
            if t1.day != t2.day:
                break
            
            # Same day: check strict overlap
            t1_end = t1.start_time * 60 + t1.duration_mins
            t2_start = t2.start_time * 60
            
            if t2_start < t1_end:
                 errors.append(f"Overlap detected on {t1.day} between Task {t1.task_id} and Task {t2.task_id}.")
                 
    return errors
