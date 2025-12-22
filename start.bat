@echo off
echo Starting AI Planner...

:: Start Backend
start cmd /k "cd /d %~dp0 && call backend\venv\Scripts\activate && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

:: Start Frontend 
cd frontend
start cmd /k "npm run dev"
