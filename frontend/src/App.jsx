import React, { useState, useEffect } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import Favorites from './components/Favorites';
import TaskBank from './components/TaskBank';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [messages, setMessages] = useState([
    { sender: 'ai', message: 'Hi there! I can help you adjust your schedule.' }
  ]);

  // Effect to load tasks on mount
  useEffect(() => {
    fetchTasks();
  }, []);

  const handleSendMessage = (text) => {
    setMessages(prev => [...prev, { sender: 'user', message: text }]);
    // Mock response for now
    setTimeout(() => {
      setMessages(prev => [...prev, { sender: 'ai', message: "I'm focusing on the schedule for now." }]);
    }, 600);
  };

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
      name: task.name || task.title,
      duration: task.duration || task.duration_mins,
      tag: task.tag || 'General',
      location: task.location || 'Home',
      priority: task.priority || 'Medium',
      is_locked: task.is_locked || false,
      day: task.day,
      start_time: task.start_time,
      end_time: task.end_time,
      comments: task.comments || ''
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
      name: task.name || task.title,
      duration: task.duration || task.duration_mins,
      tag: task.tag || 'General',
      location: 'Home', // Defaults for quick add
      priority: 'Medium',
      is_locked: false,
      comments: ''
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
      setMessages(prev => [...prev, { sender: 'ai', message: "Orchestrating your schedule..." }]);

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

      // Add Scheduler Feedback to Chat
      if (data.logic_summary) {
        setMessages(prev => [...prev, { sender: 'ai', message: `✅ Schedule Updated!\n\n${data.logic_summary}` }]);
      } else {
        setMessages(prev => [...prev, { sender: 'ai', message: "✅ Schedule Updated!" }]);
      }

      if (data.warnings && data.warnings.length > 0) {
        setMessages(prev => [...prev, { sender: 'ai', message: `⚠️ Warnings: ${data.warnings.join(', ')}` }]);
      }

    } catch (error) {
      console.error("Orchestration failed:", error);
      setMessages(prev => [...prev, { sender: 'ai', message: "❌ Orchestration failed. Please try again." }]);
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
        setMessages(prev => [...prev, { sender: 'ai', message: "Schedule cleared." }]);
      }
    } catch (error) {
      console.error("Clear failed", error);
    }
  };

  const handleTaskMove = async (taskId, newDay, newHour) => {
    console.log('Moving task', taskId, 'to', newDay, newHour);

    const taskIndex = tasks.findIndex(t => t.id === taskId);
    if (taskIndex === -1) return;

    const updatedTask = {
      ...tasks[taskIndex],
      scheduled_day: newDay,
      scheduled_hour: newHour,
      status: 'scheduled'
    };

    // Optimistic update
    const newTasks = [...tasks];
    newTasks[taskIndex] = updatedTask;
    setTasks(newTasks);

    try {
      // Persist
      await fetch('http://127.0.0.1:8000/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTask)
      });
    } catch (err) {
      console.error("Failed to move task", err);
      // Revert on failure would go here
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
          <NegotiationChat messages={messages} onSendMessage={handleSendMessage} />
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
        <CalendarView tasks={tasks} onTaskMove={handleTaskMove} />
      </section>
    </div>
  );
}

export default App;
