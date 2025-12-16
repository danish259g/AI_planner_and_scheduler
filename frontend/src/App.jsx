import React, { useState } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);

  const handleTaskInterpreted = (task) => {
    setTasks((prev) => [...prev, task]);
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Weekly Planner</h1>
      </header>

      <main className="main-layout">
        <section className="left-panel">
          <TaskInput onTaskInterpreted={handleTaskInterpreted} />
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
