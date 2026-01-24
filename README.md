# AI Weekly Planner & Scheduler

An intelligent weekly planning application that uses Generative AI (Google Gemini) to orchestrate tasks into a weekly schedule.

## Features
- **Task Bank**: Add tasks with "natural language" - the AI interprets duration and tags.
- **Orchestration**: Automatically schedules tasks into empty time slots using Gemini.
- **Interactive Calendar**: Visual representation of the weekly schedule.
- **Smart Scheduling**: Avoids overlaps and respects task durations.
- **Cognitive Profiling**: Analyzes tasks (Analytical, Creative, etc.) to optimize energy.
- **Personal Profile**: Customize your "Vibe" (Peak Energy, Scheduling Style) to tailor the schedule to your preferences.

## Prerequisites
- **Node.js** (v16+)
- **Python** (v3.10+)
- **Google Gemini API Key**: You can get one from [Google AI Studio](https://aistudio.google.com/).

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AI_planner_and_scheduler
```

### 2. Backend Setup
Navigate to the root directory and set up the Python environment.

```bash
python -m venv backend\venv
# Windows:
backend\venv\Scripts\activate
# Mac/Linux:
# source backend/venv/bin/activate

pip install -r backend/requirements.txt
```

**Configuration:**
Create a `.env` file in the `backend/` directory and add your API key:
```ini
GEMINI_API_KEY=your_api_key_here
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies.

```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Option A: Quick Start (Windows)
Run the provided batch script in the root directory:
```bash
start.bat
```

### Option B: Manual Start
You need to run the backend and frontend in separate terminals.

**Terminal 1 (Backend):**
Run from the **ROOT** directory `AI_planner_and_scheduler`:
```bash
# Ensure venv is active
# backend\venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Open your browser and navigate to `http://localhost:5173`.

## Usage
1. **Add Tasks**: Type a task (e.g., "Gym workout for 1 hour") in the "Add New Task" box.
2. **Setup Profile**: Click the User Icon to set your peak energy times and constraints.
3. **Orchestrate**: Click the **✨ Orchestrate Week** button to have AI schedule items.
4. **Chat & Negotiate**: Use the Assistant chat to ask for changes (e.g., "Move gym to Tuesday").

## Troubleshooting
- **Connection Refused**: Ensure the backend is running on port 8000.
- **Import Errors**: Make sure you run `uvicorn` from the **root** folder, not inside `backend/`.
- **API Errors**: Check your `GEMINI_API_KEY` in `backend/.env`.