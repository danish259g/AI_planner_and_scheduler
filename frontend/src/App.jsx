import React, { useState } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import Favorites from './components/Favorites';
import TaskBank from './components/TaskBank';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);

  const handleTaskInterpreted = (task) => {
    // For demo, just log it
    console.log("Task added:", task);
  };

  const handleQuickAdd = (text) => {
    console.log("Quick add:", text);
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
          <TaskBank />
        </div>
      </section>

      {/* RIGHT COLUMN: Schedule */}
      <section className="layout-schedule">
        <div style={{ padding: '1rem', borderBottom: '1px solid var(--color-border)', background: 'white' }}>
          <h3 style={{ margin: 0 }}>📅 Weekly Schedule</h3>
        </div>
        <CalendarView tasks={tasks} />
      </section>
    </div>
  );
}

export default App;
