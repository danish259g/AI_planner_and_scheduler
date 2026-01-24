import json
import shutil
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database.json'
BACKUP_PATH = Path(__file__).parent / 'database_backup.json'

def migrate():
    if not DB_PATH.exists():
        print("No database found.")
        return

    # 1. Backup
    shutil.copy(DB_PATH, BACKUP_PATH)
    print(f"Backed up DB to {BACKUP_PATH}")

    # 2. Load
    with open(DB_PATH, 'r') as f:
        data = json.loads(f.read())

    tasks = data.get("tasks", [])
    print(f"Found {len(tasks)} tasks to migrate.")

    # 3. Renumber
    new_tasks = []
    for i, t in enumerate(tasks):
        t["id"] = str(i + 1) # "1", "2", "3"
        new_tasks.append(t)
    
    data["tasks"] = new_tasks
    data["next_task_id"] = len(tasks) + 1 # Next free ID
    
    # 4. Save
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Migration complete.")
    print(f"Next Task ID set to: {data['next_task_id']}")

if __name__ == "__main__":
    migrate()
