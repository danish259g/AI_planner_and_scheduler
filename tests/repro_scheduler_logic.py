
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.optimizer import DailyBatchOptimizer, OptimizationTask, CognitiveType

def run_test():
    print("--- Running Scheduler Logic Reproduction ---")
    
    # Setup: Evening Person, Creative Tasks
    user_settings = {
        'study_start': 8,
        'study_end': 22,
        'peak_energy': 'evening', # User prefers evening
        'max_daily_hours': 10
    }
    
    # 3 hours of Essay writing (Creative/High focus)
    tasks = [
        OptimizationTask(id="1", name="Essay 1", duration_mins=60, subject="Essay", cognitive_type=CognitiveType.CREATIVE, priority="High"),
        OptimizationTask(id="2", name="Essay 2", duration_mins=60, subject="Essay", cognitive_type=CognitiveType.CREATIVE, priority="High"),
        OptimizationTask(id="3", name="Essay 3", duration_mins=60, subject="Essay", cognitive_type=CognitiveType.CREATIVE, priority="High"),
    ]
    
    optimizer = DailyBatchOptimizer("Mon", [], user_settings)
    scheduled, dropped = optimizer.solve(tasks)
    
    with open('repro.log', 'w') as f:
        f.write(f"Scheduled {len(scheduled)} tasks.\n")
        
        # Analysis
        last_end = -1.0
        consecutive = 0
        max_consecutive = 0
        
        for s in scheduled:
            msg = f"Task {s['id']}: {s['start_time']} - {s['end_time']}"
            print(msg)
            f.write(msg + "\n")
            
            # Check morning bias
            if s['start_time'] < 12:
                msg = f"  -> WARNING: Creative task scheduled in MORNING despite Evening preference."
                print(msg)
                f.write(msg + "\n")

            # Check consecutive
            # Note: The optimizer considers 15 mins (0.25) as a break.
            # So we shout count as consecutive only if gap < 0.25 strictly
            if last_end != -1 and (s['start_time'] - last_end) < (0.25 - 1e-5): 
                 # Contiguous (gap < 15m)
                 width = (s['end_time'] - s['start_time']) * 60
                 consecutive += width
            else:
                 consecutive = (s['end_time'] - s['start_time']) * 60
            
            last_end = s['end_time']
            if consecutive > max_consecutive:
                max_consecutive = consecutive
                
        f.write(f"Max Consecutive Minutes: {max_consecutive}\n")
        if max_consecutive > 90:
            f.write("FAIL: Max consecutive minutes > 90!\n")
        else:
            f.write("PASS: 90-minute limit respected.\n")

if __name__ == "__main__":
    run_test()
