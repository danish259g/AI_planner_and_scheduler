@echo off
echo Starting AI Planner Project...

echo Starting Backend on port 8000...
start "Backend" cmd /k "cd backend && call venv\Scripts\activate && python main.py"

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Done. Backend running on http://localhost:8000, Frontend on http://localhost:5173
