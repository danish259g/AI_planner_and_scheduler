# AI Weekly Planner & Scheduler

An intelligent weekly planning application that uses Generative AI (Google Gemini) to orchestrate tasks into a weekly schedule.

## Features
- **Task Bank**: Add tasks with "natural language" - the AI interprets duration and tags.
- **Orchestration**: Automatically schedules tasks into empty time slots using Gemini.
- **Interactive Calendar**: Visual representation of the weekly schedule.
- **Smart Scheduling**: Avoids overlaps and respects task durations.

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
Navigate to the backend directory and set up the Python environment.

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

**Configuration:**
Create a `.env` file in the `backend/` directory and add your API key:
```ini
GEMINI_API_KEY=your_api_key_here
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies.

```bash
cd ../frontend
npm install
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
```bash
cd backend
# Ensure venv is active
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
2. **Build Your Bank**: Add multiple tasks to the Task Bank.
3. **Orchestrate**: Click the **✨ Orchestrate Week** button in the Task Bank to have AI schedule them.
4. **Clear**: Use the "Clear" button in the schedule header to reset.

## Troubleshooting
- **Connection Refused**: Ensure the backend is running on port 8000.
- **API Errors**: Check your `GEMINI_API_KEY` in `backend/.env`.