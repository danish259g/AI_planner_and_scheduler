import streamlit as st
import pandas as pd
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from backend/.env if it exists
load_dotenv(Path(__file__).parent / "backend" / ".env")

# Add the project root to sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from backend import storage, scheduler, interpreter

# --- Setup & Styling ---
st.set_page_config(page_title="AI Weekly Planner", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em; 
    }
    .status-pending { color: orange; font-weight: bold; }
    .status-scheduled { color: green; font-weight: bold; }
    div[data-testid="stExpander"] details summary p {
        font-weight: 600;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- Constants (Favorites Data) ---
CATEGORIES = {
    "Quantitative Reasoning": {
        "tag": "Quantitative", "color": "red",
        "sub": {
            "Algebra": { "duration": 45 },
            "Word Problems": { "duration": 45 },
            "Geometry": { "duration": 45 },
            "Data Interpretation": { "duration": 45 }
        }
    },
    "Verbal Reasoning": {
        "tag": "Verbal", "color": "orange",
        "sub": {
            "Analogies": { "duration": 30 },
            "Sentence Completions": { "duration": 25 },
            "Logic & Inference": { "duration": 45 },
            "Reading Comprehension": { "duration": 50 },
            "Vocab Memorization": { "duration": 20 },
            "Reading a Book": { "duration": 30 }
        }
    },
    "English": {
        "tag": "English", "color": "blue",
        "sub": {
            "Sentence Completions": { "duration": 20 },
            "Restatements": { "duration": 20 },
            "Reading Comprehension": { "duration": 40 },
            "Vocab Memorization": { "duration": 25 },
            "Reading a Book": { "duration": 30 }
        }
    },
    "Essay Writing": {
        "tag": "Essay", "color": "green",
        "sub": {
            "Intro & Conclusion": { "duration": 30 },
            "Argumentative para": { "duration": 30 },
            "Critical Thinking para": { "duration": 30 },
            "Analyze Sample": { "duration": 30 },
            "Full-length Essay": { "duration": 35 }
        }
    },
    "Practice Modes": {
        "tag": "Simulation", "color": "purple",
        "sub": {
            "Timed Section (Quant)": { "duration": 20 },
            "Timed Section (Verbal)": { "duration": 20 },
            "Timed Section (English)": { "duration": 20 },
            "Full Simulation": { "duration": 210 }
        }
    }
}

# --- Helper Functions ---
def load_and_display_tasks():
    tasks = storage.load_tasks()
    if not tasks:
        st.info("No tasks in the bank.")
        return []
    tasks.sort(key=lambda x: x.get("status") == "scheduled")
    return tasks

async def perform_scheduling():
    with st.spinner("🤖 Orchestrating schedule..."):
        try:
            perf_data = storage.get_performance()
            user_settings = storage.get_user_settings()
            
            # Simple callback mock
            async def mock_callback(pmap): pass 

            tasks = storage.load_tasks()
            result = await scheduler.orchestrate_schedule(
                tasks, 
                performance_data=perf_data, 
                user_settings=user_settings,
                profile_update_callback=mock_callback
            )
            return result
        except Exception as e:
            st.error(f"Error during scheduling: {e}")
            return None

def save_schedule_result(result):
    if not result: return
    tasks = storage.load_tasks()
    scheduled_map = {str(item.task_id): item for item in result.schedule}
    updated_tasks = []
    
    for t in tasks:
        t_id = str(t.get("id"))
        matches = scheduled_map.get(t_id)
        if matches:
            t["scheduled_day"] = matches.day
            t["scheduled_start"] = matches.start_time
            
            duration = t.get("duration") or t.get("duration_mins") or 30
            t["scheduled_end"] = matches.start_time + (duration / 60)
            t["status"] = "scheduled"
            if getattr(matches, "rationale", None):
                t["rationale"] = matches.rationale
        else:
            t["status"] = "pending"
            t["scheduled_day"] = None
            t["scheduled_start"] = None
            t["scheduled_end"] = None
        updated_tasks.append(t)
    
    storage.save_tasks(updated_tasks)
    st.success("Schedule updated!")

async def quick_add_task(name, duration, tag):
    new_task = {
        "name": name,
        "duration": duration,
        "tag": tag,
        "status": "pending",
        "location": "Home",
        "priority": "Medium",
        "is_locked": False,
        "comments": ""
    }
    storage.add_task(new_task)
    # st.rerun() will be called by caller

# --- Main App ---

st.title("🎓 Psychometric AI Coach")

# Sidebar
page = st.sidebar.radio("Navigation", ["Tasks", "Schedule", "Profile"])

if page == "Tasks":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚡ Quick Add")
        # Favorites Implementation
        for cat_name, cat_data in CATEGORIES.items():
            with st.expander(f"{cat_name}", expanded=False):
                for sub_name, sub_data in cat_data["sub"].items():
                    if st.button(f"{sub_name} ({sub_data['duration']}m)", key=f"add_{cat_name}_{sub_name}"):
                        asyncio.run(quick_add_task(sub_name, sub_data['duration'], cat_data['tag']))
                        st.rerun()

        st.divider()
        st.subheader("🔒 Fixed Commitments")
        # Constraint Form
        with st.form("constraint_form"):
            c_name = st.text_input("Name", placeholder="e.g. Gym")
            c_day = st.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            c1, c2 = st.columns(2)
            c_start = c1.number_input("Start (Hr)", 0, 23, 18)
            c_end = c2.number_input("End (Hr)", 0, 23, 19)
            
            if st.form_submit_button("Add Commitment"):
                new_constraint = {
                    "name": c_name,
                    "day": c_day,
                    "start": c_start,
                    "end": c_end
                }
                settings = storage.get_user_settings()
                settings["constraints"].append(new_constraint)
                storage.update_user_settings(settings)
                st.success("Commitment added!")
                st.rerun()

    with col2:
        st.subheader("Task Bank")
        tasks = load_and_display_tasks()
        
        # Display Tasks
        if tasks:
            for t in tasks:
                # Simple Card Style
                with st.container():
                    c1, c2, c3 = st.columns([0.7, 0.2, 0.1])
                    t_name = t.get("name") or t.get("title")
                    t_dur = t.get("duration") or t.get("duration_mins")
                    t_status = t.get("status")
                    
                    status_icon = "✅" if t_status == "scheduled" else "⏳"
                    
                    c1.markdown(f"**{t_name}** <span style='color:gray; font-size:0.8em'>({t_dur}m)</span>", unsafe_allow_html=True)
                    if t_status == "scheduled":
                         c1.caption(f"📍 {t.get('scheduled_day')} @ {t.get('scheduled_start')}:00")
                    
                    c2.write(f"{status_icon}")
                    if c3.button("🗑️", key=f"del_{t.get('id')}"):
                        storage.delete_task(t.get("id"))
                        st.rerun()
                    st.divider()
        else:
            st.info("No tasks yet. Use Quick Add!")

elif page == "Schedule":
    st.header("Weekly Schedule")
    
    col_act, col_clr = st.columns([1, 4])
    if col_act.button("🚀 Orchestrate", type="primary"):
        res = asyncio.run(perform_scheduling())
        save_schedule_result(res)
        st.rerun()
        
    if col_clr.button("Clear Schedule"):
        storage.clear_schedule_data()
        st.rerun()
    
    st.divider()
    
    # Schedule Visualization (Columns)
    tasks = storage.load_tasks()
    scheduled_tasks = [t for t in tasks if t.get("status") == "scheduled"]
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
            # Get tasks for this day
            # Note: storage might save full day names "Monday", let's handle loose matching if needed
            day_tasks = [t for t in scheduled_tasks if t.get("scheduled_day", "").startswith(day)]
            day_tasks.sort(key=lambda x: x.get("scheduled_start", 0))
            
            for t in day_tasks:
                start = t.get("scheduled_start", 0)
                end = t.get("scheduled_end", 0)
                name = t.get("name") or t.get("title")
                type_ = t.get("cognitive_type", "General")
                
                # Dynamic coloring based on type (simple mapping)
                bg_color = "#333"
                if "Quant" in type_: bg_color = "rgba(255, 75, 75, 0.2)"
                elif "Verbal" in type_: bg_color = "rgba(255, 165, 0, 0.2)"
                elif "English" in type_: bg_color = "rgba(0, 0, 255, 0.2)"
                
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 5px; border-radius: 5px; margin-bottom: 5px; font-size: 0.8em;">
                    <strong>{start:.0f}:00</strong><br>{name}
                </div>
                """, unsafe_allow_html=True)

elif page == "Profile":
    st.header("👤 User Profile")
    
    settings = storage.get_user_settings()
    
    with st.form("profile_form"):
        st.subheader("Personal Details")
        s_username = st.text_input("Display Name", value=settings.get("username", ""))
        
        c1, c2 = st.columns(2)
        s_peak = c1.selectbox("Peak Energy Time", ["morning", "afternoon", "evening"], 
                            index=["morning", "afternoon", "evening"].index(settings.get("peak_energy", "morning")))
        
        s_style = c2.selectbox("Scheduling Style", ["spread", "batch"], 
                             index=["spread", "batch"].index(settings.get("scheduling_style", "spread")))
        
        st.subheader("Study Hours")
        c3, c4, c5 = st.columns(3)
        s_start = c3.number_input("Start Hour", 0, 23, settings.get("study_start", 8))
        s_end = c4.number_input("End Hour", 0, 23, settings.get("study_end", 22))
        s_limit = c5.number_input("Daily Limit (Hrs)", 1, 16, settings.get("max_daily_hours", 8))
        
        st.subheader("Manage Commitments")
        # List existing constraints with delete capability
        constraints = settings.get("constraints", [])
        if constraints:
            for i, c in enumerate(constraints):
                col_c1, col_c2 = st.columns([4, 1])
                col_c1.text(f"{c['name']} ({c['day']} {c['start']}-{c['end']})")
                # We can't delete easily inside a form without rerunning, so maybe just show them here
                # Or use a checkbox to mark for deletion
        else:
            st.caption("No fixed commitments added yet.")

        if st.form_submit_button("Save Profile"):
            new_settings = settings.copy()
            new_settings.update({
                "username": s_username,
                "peak_energy": s_peak,
                "scheduling_style": s_style,
                "study_start": s_start,
                "study_end": s_end,
                "max_daily_hours": s_limit
            })
            storage.update_user_settings(new_settings)
            st.success("Profile saved!")
