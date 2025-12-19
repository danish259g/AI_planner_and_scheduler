import React, { useState, useEffect } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import Favorites from './components/Favorites';
import TaskBank from './components/TaskBank';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);

  // Effect to load tasks on mount
  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/tasks');
      if (res.ok) {
        const data = await res.json();
        setTasks(data);
      }
    } catch (err) {
      console.error("Failed to fetch tasks", err);
    }
  };

  const handleTaskInterpreted = async (task) => {
    // Optimistic or wait? We wait as per plan.
    const newTask = {
      id: Date.now(), // Still generate temp ID or let backend do it? 
      // Backend expects ID. Let's send one.
      title: task.title,
      duration_mins: task.duration_mins,
      tag: 'New'
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask)
      });
      if (res.ok) {
        const savedTask = await res.json();
        setTasks(prev => [...prev, savedTask]);
      }
    } catch (err) {
      console.error("Failed to add task", err);
    }
  };

  const handleQuickAdd = async (task) => {
    const newTask = {
      id: Date.now(),
      title: task.title,
      duration_mins: task.duration_mins,
      tag: task.tag
    };
    try {
      const res = await fetch('http://127.0.0.1:8000/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask)
      });
      if (res.ok) {
        const savedTask = await res.json();
        setTasks(prev => [...prev, savedTask]);
      }
    } catch (err) {
      console.error("Failed to quick add task", err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tasks/${taskId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setTasks(prev => prev.filter(t => t.id !== taskId));
      }
    } catch (err) {
      console.error("Failed to delete task", err);
    }
  };

  const handleOrchestrate = async () => {
    try {
      console.log("Orchestrating tasks...");
      // No body needed now, backend reads from DB
      const response = await fetch('http://127.0.0.1:8000/api/schedule/generate', {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Orchestration result:", data);

      // Update tasks with the new schedule info
      setTasks(data.tasks);

    } catch (error) {
      console.error("Orchestration failed:", error);
    }
  };

  const handleClearSchedule = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/schedule/clear', {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks);
      }
    } catch (error) {
      console.error("Clear failed", error);
    }
  };

  return (
    <div className="app-container">
      {/* LEFT COLUMN: Inputs & Assistant */}
      <section className="layout-sidebar">

        {/* Add Task */}
        <div className="glass-panel">
          <h3>
            <span>➕</span> Add New Task
          </h3>
          <TaskInput onTaskInterpreted={handleTaskInterpreted} />
        </div>

        {/* Quick Add */}
        <div className="glass-panel">
          <h3>
            <span>⚡</span> Quick Add
          </h3>
          <Favorites onQuickAdd={handleQuickAdd} />
        </div>

        {/* Assistant (Moved here) */}
        <div className="glass-panel flex-grow">
          <h3>
            <span>🤖</span> Assistant
          </h3>
          <NegotiationChat />
        </div>

      </section>

      {/* CENTER COLUMN: Task Bank */}
      <section className="layout-center">
        <div className="glass-panel flex-grow">
          <h3>
            <span>📥</span> Task Bank
          </h3>
          <TaskBank tasks={tasks} onDeleteTask={handleDeleteTask} onOrchestrate={handleOrchestrate} />
        </div>
      </section>

      {/* RIGHT COLUMN: Schedule */}
      <section className="layout-schedule">
        <div style={{
          padding: '1rem',
          borderBottom: '1px solid var(--color-border)',
          background: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3 style={{ margin: 0 }}>📅 Weekly Schedule</h3>
          <button
            onClick={handleClearSchedule}
            className="clear-btn"
            style={{
              background: 'transparent',
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              padding: '0.4rem 0.8rem',
              fontSize: '0.85rem',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-primary)';
              e.currentTarget.style.color = 'var(--color-primary)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            Clear
          </button>
        </div>
        <CalendarView tasks={tasks} />
      </section>
    </div>
  );
}

export default App;
