import React, { useState } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import Favorites from './components/Favorites';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);

  const handleTaskInterpreted = (task) => {
    setTasks((prev) => [...prev, task]);
  };

  const handleQuickAdd = async (text) => {
    // Simulate quick add by calling interpret (or just add directly)
    // For now, we reuse the interpreter endpoint flow but programmatically
    try {
      const response = await fetch('/api/interpret', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: text }),
      });
      const data = await response.json();
      handleTaskInterpreted(data);
    } catch (error) {
      console.error("Quick add failed", error);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Weekly Planner</h1>
      </header>

      <main className="main-layout">
        <section className="left-panel">
          <TaskInput onTaskInterpreted={handleTaskInterpreted} />
          <Favorites onQuickAdd={handleQuickAdd} />
          <NegotiationChat />
        </section>

        <section className="right-panel">
          <CalendarView tasks={tasks} />
        </section>
      </main>
    </div>
  );
}

export default App;
