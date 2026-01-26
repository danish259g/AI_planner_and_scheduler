import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.optimizer import DailyBatchOptimizer, OptimizationTask, CognitiveType

def test_analytical_placement():
    print("\n--- Test 1: Analytical Placement ---")
    # Analytical task should prefer ~13.5 (1:30 PM)
    optimizer = DailyBatchOptimizer(
        day_name="Mon", 
        constraints=[], 
        user_settings={"study_start": 8, "study_end": 20, "peak_energy": "morning"}
    )
    
    task = OptimizationTask(
        id="1", name="Hard Math", duration_mins=60, 
        subject="Quantitative", cognitive_type=CognitiveType.ANALYTICAL, 
        priority="Medium"
    )
    
    results = optimizer.solve([task])
    
    if results:
        start = results[0]['start_time']
        print(f"Task placed at: {start}")
        # 13.5 is the peak. 
        # With "Morning" preference, earlier slots get +50 (<12).
        # Analytical peak gets +50 (near 13.5).
        # If morning score (50) == Analytical score (50), greedy picks first (Morning).
        # Let's see which wins.
        if 13.0 <= start <= 14.0:
            print("SUCCESS: Analytical Peak was felt!")
        else:
            print(f"NOTE: Placed at {start}. (Possibly Morning Preference dominated?)")
    else:
        print("FAILED: No slot found")

def test_90_min_law():
    print("\n--- Test 2: 90-Minute Law ---")
    optimizer = DailyBatchOptimizer(
        day_name="Mon", constraints=[], 
        user_settings={"study_start": 8, "study_end": 20}
    )
    
    # 3 Math tasks, 45 mins each. 
    # 1st: 8:00 - 8:45
    # 2nd: 8:45 - 9:30
    # 3rd: Should be BLOCKED or pushed significantly?
    # Total consecutive = 90. Max = 90.
    # So 3rd task (starting at 9:30) would make it 135 mins. Should trigger penalty.
    
    tasks = [
        OptimizationTask("1", "Math 1", 45, "Quant", CognitiveType.ANALYTICAL, "Medium"),
        OptimizationTask("2", "Math 2", 45, "Quant", CognitiveType.ANALYTICAL, "Medium"),
        OptimizationTask("3", "Math 3", 45, "Quant", CognitiveType.ANALYTICAL, "Medium"),
    ]
    
    results = optimizer.solve(tasks)
    results.sort(key=lambda x: x['start_time'])
    
    print(f"Results for 90-Min Law:")
    for r in results:
        print(f"Task {r['id']}: {r['start_time']} - {r['end_time']}")
        
    # Check gap between 2 and 3
    if len(results) == 3:
        t2_end = results[1]['end_time']
        t3_start = results[2]['start_time']
        gap = t3_start - t2_end
        if gap > 0:
            print(f"SUCCESS: Gap enacted! ({gap*60} mins)")
        else:
            print("FAIL: No gap, laws ignored.")

def test_priority_domination():
    print("\n--- Test 3: Priority Domination ---")
    # High Priority General vs Medium Priority Analytical (who wants 13.5)
    # If High Prio General takes 13.5, then Optimization is "Working" (Priority wins) 
    # but maybe not "Smart" (General could have gone anywhere).
    
    optimizer = DailyBatchOptimizer(
        day_name="Mon", constraints=[], 
        user_settings={"study_start": 13, "study_end": 15, "peak_energy": "afternoon"} # Constrained window to force conflict
    )
    
    tasks = [
        OptimizationTask("G", "General High", 60, "Gen", CognitiveType.GENERAL, "High"),
        OptimizationTask("A", "Analytical Med", 60, "Quant", CognitiveType.ANALYTICAL, "Medium"),
    ]
    
    results = optimizer.solve(tasks)
    results.sort(key=lambda x: x['start_time'])
    
    for r in results:
        print(f"{r['id']}: {r['start_time']} ({r['end_time']})")
        
    # Ideally: General takes 14.0, Analytical takes 13.0?
    # Or General takes 13.0 because it goes first?

if __name__ == "__main__":
    test_analytical_placement()
    test_90_min_law()
    test_priority_domination()
