import sys
import os
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.optimizer import DailyBatchOptimizer, OptimizationTask, CognitiveType

def reproduce_blank_issue():
    print("\n--- Simulating Blank Schedule Issue ---")
    
    # Scene: 
    # User has set very strict limits (e.g. 2 hours max) but has 3 hours of work.
    # Optimizer has strict laws (90 min global limit).
    # If the optimizer fails to fit tasks, it returns an empty list.
    
    user_settings = {
        "study_start": 8, 
        "study_end": 22, 
        "max_daily_hours": 1, # STRICT LIMIT: Only 1 hour allowed
        "peak_energy": "morning"
    }
    
    # Task: 2 hours long.
    # Should get DROPPED because 2h > 1h limit.
    tasks = [
        OptimizationTask("1", "Long Task", 120, "Subject", CognitiveType.ANALYTICAL, "High")
    ]
    
    optimizer = DailyBatchOptimizer("Mon", [], user_settings)
    results, dropped = optimizer.solve(tasks)
    
    print(f"Scheduled Count: {len(results)}")
    print(f"Dropped Count: {len(dropped)}")
    
    if dropped:
        print("SUCCESS: Dropped tasks captured:")
        for d in dropped:
            print(f"- {d['reason']}")
    else:
        print("FAILED: No dropped tasks reported (or everything fit).")

if __name__ == "__main__":
    reproduce_blank_issue()
