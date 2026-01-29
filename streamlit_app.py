import streamlit as st
import pandas as pd
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from backend/.env if it exists, for local dev
load_dotenv(Path(__file__).parent / "backend" / ".env")

# Add the project root to sys.path so we can import backend modules
# Assuming this file is in the root of the project
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from backend import storage, scheduler, interpreter

# --- Setup & Styling ---
st.set_page_config(page_title="AI Weekly Planner", page_icon="📅", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .status-pending { color: orange; font-weight: bold; }
    .status-scheduled { color: green; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def load_and_display_tasks():
    tasks = storage.load_tasks()
    if not tasks:
        st.info("No tasks in the bank.")
        return []
    
    # Sort: Pending first, then Scheduled
    tasks.sort(key=lambda x: x.get("status") == "scheduled")
    return tasks

async def perform_interpretation(text):
    with st.spinner(" Interpreting task..."):
        try:
            return await interpreter.interpret_task(text)
        except Exception as e:
            st.error(f"Error interpreting task: {e}")
            return None

async def perform_scheduling(current_tasks, user_feedback=None):
    with st.spinner("🤖 Orchestrating schedule... (this calls Gemini)"):
        try:
            perf_data = storage.get_performance()
            user_settings = storage.get_user_settings()
            
            # Simple callback mock
            async def mock_callback(pmap):
                pass 

            if user_feedback:
                 result = await scheduler.orchestrate_schedule(
                    current_tasks, 
                    user_feedback=user_feedback,
                    performance_data=perf_data, 
                    user_settings=user_settings,
                    profile_update_callback=mock_callback
                )
            else:
                result = await scheduler.orchestrate_schedule(
                    current_tasks, 
                    performance_data=perf_data, 
                    user_settings=user_settings,
                    profile_update_callback=mock_callback
                )
            return result
        except Exception as e:
            st.error(f"Error during scheduling: {e}")
            return None

def save_schedule_result(result, all_tasks):
    # Logic copied from backend/main.py essentially
    if not result: return

    scheduled_map = {str(item.task_id): item for item in result.schedule}
    updated_tasks = []
    
    for t in all_tasks:
        t_id = str(t.get("id"))
        matches = scheduled_map.get(t_id)
        if matches:
            t["scheduled_day"] = matches.day
            t["scheduled_start"] = matches.start_time
            if "duration" in t:
                duration = t["duration"] 
            elif "duration_mins" in t:
                 duration = t["duration_mins"]
            else:
                 duration = 30 # fallback
            
            t["scheduled_end"] = matches.start_time + (duration / 60)
            t["status"] = "scheduled"
            if getattr(matches, "rationale", None):
                t["rationale"] = matches.rationale
        else:
            # If we just re-generated, and it was previously scheduled but now dropped -> pending
            t["status"] = "pending"
            t["scheduled_day"] = None
            t["scheduled_start"] = None
            t["scheduled_end"] = None
        
        # Injected tasks logic is complex to replicate exactly without code duplication,
        # for now let's stick to updating existing.
        updated_tasks.append(t)
    
    storage.save_tasks(updated_tasks)
    st.success("Schedule updated!")


# --- Main App Structure ---

st.title("📅 AI Weekly Planner")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["Tasks", "Schedule", "Settings"])

if page == "Tasks":
    st.header("Task Bank")
    
    # Input
    with st.form("new_task_form"):
        raw_text = st.text_input("Add a new task (natural language):", placeholder="e.g., 'Study Math for 2 hours on Tuesday'")
        submitted = st.form_submit_button("Add Task")
        
        if submitted and raw_text:
            # Create an event loop for the async call
            try:
                interpreted_data = asyncio.run(perform_interpretation(raw_text))
                if interpreted_data:
                    # Convert to dict and save
                    new_task_dict = interpreted_data.dict()
                    # Storage handles ID assignment
                    storage.add_task(new_task_dict)
                    st.success(f"Added: {interpreted_data.name}")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to add task: {e}")

    st.divider()
    
    # Display
    tasks = load_and_display_tasks()
    
    # Convert to DataFrame for nicer display
    if tasks:
        df_data = []
        for t in tasks:
            df_data.append({
                "ID": t.get("id"),
                "Name": t.get("name") or t.get("title"),
                "Duration (m)": t.get("duration") or t.get("duration_mins"),
                "Status": t.get("status"),
                "Day": t.get("scheduled_day") if t.get("status") == "scheduled" else t.get("day"),
                "Type": t.get("cognitive_type"),
                "Action": "Delete" # Placeholder
            })
        
        df = pd.DataFrame(df_data)
        
        # Display using columns for simple list
        for index, row in df.iterrows():
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            with c1:
                st.write(f"**{row['Name']}**")
                if row['Status'] == 'scheduled':
                     st.caption(f"📍 {row['Day']} @ {row.get('Day')} (This display logic is simple)")
            with c2:
                st.write(f"{row['Duration (m)']}m")
            with c3:
                status_color = "green" if row['Status'] == "scheduled" else "orange"
                st.markdown(f":{status_color}[{row['Status']}]")
            with c4:
                st.write(row['Type'])
            with c5:
                if st.button("🗑️", key=f"del_{row['ID']}"):
                    storage.delete_task(row['ID'])
                    st.rerun()

elif page == "Schedule":
    st.header("Orchestration")
    
    tasks = storage.load_tasks()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🚀 Generate Full Schedule", type="primary"):
            try:
                result = asyncio.run(perform_scheduling(tasks))
                if result:
                    save_schedule_result(result, tasks)
                    st.rerun()
            except Exception as e:
                st.error(f"Scheduling failed: {e}")

    st.divider()
    
    # Schedule Visualization
    scheduled_tasks = [t for t in tasks if t.get("status") == "scheduled"]
    
    if not scheduled_tasks:
        st.info("No tasks scheduled yet. Click Generate!")
    else:
        # Group by day
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Simple column view
        cols = st.columns(7)
        for i, day in enumerate(days):
            day_tasks = [t for t in scheduled_tasks if t.get("scheduled_day") == day]
            day_tasks.sort(key=lambda x: x.get("scheduled_start", 0))
            
            with cols[i]:
                st.markdown(f"#### {day[:3]}")
                for t in day_tasks:
                    start = t.get("scheduled_start", 0)
                    end = t.get("scheduled_end", 0)
                    name = t.get("name") or t.get("title")
                    st.success(f"**{start:.1f}-{end:.1f}**\n{name}")

    st.divider()
    st.subheader("Negotiate")
    user_input = st.text_input("Ask for changes (e.g. 'Move Math to Tuesday'):")
    if st.button("Update Schedule"):
        if user_input:
            try:
                result = asyncio.run(perform_scheduling(tasks, user_feedback=user_input))
                if result:
                    save_schedule_result(result, tasks)
                    st.rerun()
            except Exception as e:
                 st.error(f"Negotiation failed: {e}")

elif page == "Settings":
    st.header("User Settings")
    current_settings = storage.get_user_settings()
    
    with st.form("settings_form"):
        # Example settings fields
        start_hour = st.number_input("Start Hour", value=current_settings.get("start_hour", 8))
        end_hour = st.number_input("End Hour", value=current_settings.get("end_hour", 22))
        
        if st.form_submit_button("Save Settings"):
            new_settings = current_settings.copy()
            new_settings["start_hour"] = start_hour
            new_settings["end_hour"] = end_hour
            storage.update_user_settings(new_settings)
            st.success("Settings saved!")
