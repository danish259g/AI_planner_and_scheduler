import React, { useState } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import Favorites from './components/Favorites';
import TaskBank from './components/TaskBank';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([
    { id: 1, title: 'Draft Q1 Report', duration_mins: 120, tag: 'Work' },
    { id: 2, title: 'Email Marketing Team', duration_mins: 30, tag: 'Comms' },
    { id: 3, title: 'Code Review', duration_mins: 60, tag: 'Dev' },
    { id: 4, title: 'Gym - Leg Day', duration_mins: 90, tag: 'Health' },
  ]);

  const handleTaskInterpreted = (task) => {
    // Add the new task to the list
    setTasks(prev => [...prev, {
      id: Date.now(), // simple unique id
      title: task.title,
      duration_mins: task.duration_mins,
      tag: 'New' // default tag for now
    }]);
  };

  const handleQuickAdd = (task) => {
    console.log("Quick add:", task);
    setTasks(prev => [...prev, {
      id: Date.now(),
      title: task.title,
      duration_mins: task.duration_mins,
      tag: task.tag
    }]);
  };

  const handleDeleteTask = (taskId) => {
    setTasks(prev => prev.filter(t => t.id !== taskId));
  };

  const handleOrchestrate = async () => {
    try {
      console.log("Orchestrating tasks...", tasks);
      // We only want to send tasks that are not yet scheduled or fully send all to re-optimize?
      // Let's send all for now.
      const response = await fetch('http://127.0.0.1:8000/api/schedule/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tasks)
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

  const handleClearSchedule = () => {
    setTasks(prev => prev.map(t => {
      const { scheduled_day, scheduled_hour, ...rest } = t;
      return { ...rest, status: 'pending' };
    }));
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
