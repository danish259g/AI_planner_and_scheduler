import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.optimizer import DailyBatchOptimizer, OptimizationTask, CognitiveType

def test_violation():
    print("\n--- Test: 5x30min Task Chain (Expect Break) ---")
    
    # Settings from user: Evening Person (-10 in morning)
    user_settings = {
        "study_start": 8, 
        "study_end": 22, 
        "max_daily_hours": 5,
        "peak_energy": "evening" 
    }
    
    # 5 Tasks, 30 mins each. All Creative (prefer morning +40).
    # Net Morning Score: +40 - 10 = +30.
    # Net Evening Score: 0/0 + 25 = +25.
    # So Morning is PREFERRED (+30 > +25).
    # This explains why they are in morning.
    
    tasks = [
        OptimizationTask("1", "Task 1", 30, "Subj", CognitiveType.CREATIVE, "Medium"),
        OptimizationTask("2", "Task 2", 30, "Subj", CognitiveType.CREATIVE, "Medium"),
        OptimizationTask("3", "Task 3", 30, "Subj", CognitiveType.CREATIVE, "Medium"),
        OptimizationTask("4", "Task 4", 30, "Subj", CognitiveType.CREATIVE, "Medium"), # Should Break
        OptimizationTask("5", "Task 5", 30, "Subj", CognitiveType.CREATIVE, "Medium"),
    ]
    
    optimizer = DailyBatchOptimizer("Tue", [], user_settings)
    results, dropped = optimizer.solve(tasks)
    
    results.sort(key=lambda x: x['start_time'])
    
    print("Timeline:")
    for r in results:
        print(f"{r['id']}: {r['start_time']} - {r['end_time']}")
        
    # Validation
    if len(results) >= 4:
        # Check gap between 3 and 4
        end3 = results[2]['end_time']
        start4 = results[3]['start_time']
        gap = (start4 - end3) * 60
        print(f"Gap between 3 and 4: {gap:.1f} min")
        
        if gap >= 15:
            print("SUCCESS: Break enforced.")
        else:
            print("FAILURE: No break.")

if __name__ == "__main__":
    test_violation()
