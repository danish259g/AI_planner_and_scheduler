import React, { useState, useEffect } from 'react';
import TaskInput from './components/TaskInput';
import CalendarView from './components/CalendarView';
import NegotiationChat from './components/NegotiationChat';
import Favorites from './components/Favorites';
import TaskBank from './components/TaskBank';
import PerformanceDashboard from './components/PerformanceDashboard';
import TaskEditModal from './components/TaskEditModal';
import ConstraintEditModal from './components/ConstraintEditModal';
import UserProfileModal from './components/UserProfileModal';

import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [isVibeOpen, setIsVibeOpen] = useState(false);

  const [messages, setMessages] = useState([
    { sender: 'ai', message: 'System Ready. Logging events...' }
  ]);
  const [performance, setPerformance] = useState({
    Quantitative: { score: 0, self_eval: 5, count: 0 },
    Verbal: { score: 0, self_eval: 5, count: 0 },
    English: { score: 0, self_eval: 5, count: 0 },
    Essay: { score: 0, self_eval: 5, count: 0 }
  });
  const [sidebarTab, setSidebarTab] = useState('chat'); // 'chat' or 'performance'
  const [userSettings, setUserSettings] = useState({
    username: '',
    study_start: 8,
    study_end: 22,
    max_daily_hours: 8,
    peak_energy: 'morning', // 'morning', 'afternoon', 'evening'
    scheduling_style: 'spread', // 'spread', 'batch'
    constraints: []
  });
  const [vibeTab, setVibeTab] = useState('vibe'); // 'vibe', 'hours', 'constraints'
  const [editingTask, setEditingTask] = useState(null);
  const [editingConstraint, setEditingConstraint] = useState(null); // { constraint, index }
  const [isOrchestrating, setIsOrchestrating] = useState(false);

  // Effect to load tasks on mount
  useEffect(() => {
    fetchTasks();

    fetchPerformance();
    fetchSettings();
  }, []);

  const fetchPerformance = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/performance`);
      if (res.ok) {
        const data = await res.json();
        setPerformance(data);
      }
    } catch (err) {
      console.error("Failed to fetch performance", err);
    }
  };



  const fetchSettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/settings`);
      if (res.ok) {
        const data = await res.json();
        setUserSettings(data);
      }
    } catch (err) {
      console.error("Failed to fetch settings", err);
    }
  };

  const handleSaveProfile = async () => {
    try {
      // Save Settings
      await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userSettings)
      });

      setIsVibeOpen(false);
      setMessages(prev => [...prev, { sender: 'ai', message: "Strategy updated! I'll respect your constraints and study hours in the next orchestration." }]);
    } catch (err) {
      console.error("Failed to save profile or settings", err);
    }
  };



  const fetchTasks = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`);
      if (res.ok) {
        const data = await res.json();
        setTasks(data);
      }
    } catch (err) {
      console.error("Failed to fetch tasks", err);
    }
  };

  const handleTaskInterpreted = async (task) => {
    // The backend's /api/interpret ALREADY saved the task to DB and returned the full object with ID.
    // So we just update the UI state directly. No need to POST again.
    console.log("Adding interpreted task from backend:", task);
    setTasks(prev => [...prev, task]);
  };

  const handleQuickAdd = async (task) => {
    const newTask = {
      id: null, // Server will assign ID
      name: task.name || task.title,
      duration: task.duration || task.duration_mins,
      status: 'pending',
      tag: task.tag || 'General',
      location: 'Home',
      priority: 'Medium',
      is_locked: false,
      comments: ''
    };
    try {
      const res = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask)
      });
      if (res.ok) {
        const savedTask = await res.json();
        // Backend returns the full task with the new ID
        setTasks(prev => [savedTask, ...prev]);
      }
    } catch (err) {
      console.error("Failed to quick add task", err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
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
    if (isOrchestrating) return;
    try {
      setIsOrchestrating(true);
      setMessages(prev => [...prev, { sender: 'ai', message: "Orchestrating your schedule..." }]);

      const response = await fetch(`${API_BASE}/api/schedule/generate`, {
        method: 'POST'
      });

      if (!response.ok) {
        if (response.status === 503) {
          setMessages(prev => [...prev, { sender: 'ai', message: "⚠️ Quota Limit: The AI service is currently overloaded. Please wait 60 seconds and try again." }]);
          return;
        }
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
      setMessages(prev => [...prev, { sender: 'ai', message: "❌ Orchestration failed. Please try again later." }]);
    } finally {
      setIsOrchestrating(false);
    }
  };

  const handleClearSchedule = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/schedule/clear`, {
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

  const handleUpdateTask = async (taskId, updates) => {
    const taskIndex = tasks.findIndex(t => String(t.id) === String(taskId));
    if (taskIndex === -1) return;

    const originalTask = tasks[taskIndex];
    const updatedTask = { ...originalTask, ...updates };
    console.log("Updating task:", taskId, updates, updatedTask);

    // Recalculate scheduled_end if start or duration changed
    if (updatedTask.scheduled_start !== undefined && (updatedTask.duration || originalTask.duration)) {
      const dur = updatedTask.duration || originalTask.duration;
      updatedTask.scheduled_end = updatedTask.scheduled_start + (dur / 60);
    }

    // Optimistic update
    const newTasks = [...tasks];
    newTasks[taskIndex] = updatedTask;
    setTasks(newTasks);

    try {
      await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTask)
      });
    } catch (err) {
      console.error("Failed to update task", err);
    }
  };

  const handleUpdatePerformance = async (category, score, self_eval) => {
    try {
      const res = await fetch(`${API_BASE}/api/performance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, score, self_eval })
      });
      if (res.ok) {
        const data = await res.json();
        setPerformance(data);
      }
    } catch (err) {
      console.error("Failed to update performance", err);
    }
  };

  const handleResetPerformance = async () => {
    if (!window.confirm("Are you sure you want to reset all performance data? This cannot be undone.")) return;
    try {
      const res = await fetch(`${API_BASE}/api/performance/reset`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        setPerformance(data);
      }
    } catch (err) {
      console.error("Failed to reset performance", err);
    }
  };

  const handleTaskMove = async (taskId, newDay, newHour) => {
    handleUpdateTask(taskId, {
      scheduled_day: newDay,
      scheduled_start: newHour,
      status: 'scheduled'
    });
  };

  const handleUpdateConstraint = async (idx, newConstraint) => {
    const newConstraints = [...userSettings.constraints];
    newConstraints[idx] = newConstraint;
    const newSettings = { ...userSettings, constraints: newConstraints };
    setUserSettings(newSettings);

    // Save to backend
    fetch('http://127.0.0.1:8000/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    });
  };

  const handleDeleteConstraint = async (idx) => {
    const newConstraints = userSettings.constraints.filter((_, i) => i !== idx);
    const newSettings = { ...userSettings, constraints: newConstraints };
    setUserSettings(newSettings);

    // Save to backend
    fetch(`${API_BASE}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    });
  };

  return (
    <div className="app-container">
      {/* LEFT COLUMN: Inputs & Assistant */}
      <section className="layout-sidebar">
        <div style={{ marginBottom: '1.5rem', padding: '0 0.5rem' }}>
          <h1 style={{ fontSize: '1.5rem', margin: 0, color: 'var(--color-primary)', letterSpacing: '-0.02em' }}>🎓 Psychometric AI Coach</h1>
          {userSettings.username && (
            <p style={{ margin: '8px 0 0 0', fontSize: '0.95rem', color: '#64748b', fontWeight: 500 }}>
              Welcome back, <span style={{ color: 'var(--color-primary)', fontWeight: 700 }}>{userSettings.username}</span>
            </p>
          )}
        </div>

        {/* Fixed Commitments */}
        <div className="glass-panel">
          <h3>
            <span>🔒</span> Fixed Commitments
          </h3>
          <TaskInput
            onAddConstraint={(c) => {
              const newSettings = { ...userSettings, constraints: [...userSettings.constraints, c] };
              setUserSettings(newSettings);
              // Save to backend
              fetch(`${API_BASE}/api/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newSettings)
              });
            }}
          />
        </div>

        {/* Quick Add */}
        <div className="glass-panel">
          <h3>
            <span>⚡</span> Quick Add
          </h3>
          <Favorites onQuickAdd={handleQuickAdd} />
        </div>



        {/* Toggle Sidebar Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '1rem' }}>
          <button
            className={`tab-btn ${sidebarTab === 'chat' ? 'active' : ''}`}
            onClick={() => setSidebarTab('chat')}
            style={{
              flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid var(--color-border)',
              backgroundColor: sidebarTab === 'chat' ? 'var(--color-primary)' : 'white',
              color: sidebarTab === 'chat' ? 'white' : 'var(--text-main)',
              cursor: 'pointer', fontWeight: 600
            }}
          >
            🤖 Assistant
          </button>
          <button
            className={`tab-btn ${sidebarTab === 'performance' ? 'active' : ''}`}
            onClick={() => setSidebarTab('performance')}
            style={{
              flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid var(--color-border)',
              backgroundColor: sidebarTab === 'performance' ? 'var(--color-primary)' : 'white',
              color: sidebarTab === 'performance' ? 'white' : 'var(--text-main)',
              cursor: 'pointer', fontWeight: 600
            }}
          >
            📊 Performance
          </button>
        </div>

        {sidebarTab === 'chat' ? (
          <div className="glass-panel flex-grow">
            <h3>
              <span>🤖</span> Assistant
            </h3>
            <NegotiationChat messages={messages} />
          </div>
        ) : (
          <PerformanceDashboard
            performance={performance}
            onUpdate={handleUpdatePerformance}
            onReset={handleResetPerformance}
          />
        )}

      </section>

      {/* CENTER COLUMN: Task Bank (Now empty or removed) */}
      <section className="layout-center">
        <div className="glass-panel flex-grow">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Here is your task bank!</h3>
            <button
              className="profile-icon-btn"
              onClick={() => setIsVibeOpen(true)}
              title="User Profile"
              style={{
                background: 'white', border: '2px solid var(--color-primary)', width: '40px', height: '40px',
                borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.2rem', cursor: 'pointer', transition: 'all 0.2s', color: 'var(--color-primary)'
              }}
              onMouseOver={(e) => { e.currentTarget.style.background = 'var(--color-primary)'; e.currentTarget.style.color = 'white'; }}
              onMouseOut={(e) => { e.currentTarget.style.background = 'white'; e.currentTarget.style.color = 'var(--color-primary)'; }}
            >
              👤
            </button>
          </div>

          <div className="task-bank-list" style={{ flexGrow: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
            <TaskBank
              tasks={tasks}
              onDeleteTask={handleDeleteTask}
              onOrchestrate={handleOrchestrate}
              onTaskUpdate={handleUpdateTask}
              isOrchestrating={isOrchestrating}
            />
          </div>
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
        <CalendarView
          tasks={tasks}
          userSettings={userSettings}
          onTaskMove={handleTaskMove}
          onTaskUpdate={handleUpdateTask}
          onTaskClick={setEditingTask}
          onConstraintClick={(c, idx) => setEditingConstraint({ constraint: c, index: idx })}
        />
      </section>

      {editingTask && (
        <TaskEditModal
          task={editingTask}
          onClose={() => setEditingTask(null)}
          onUpdateTask={handleUpdateTask}
          onUpdatePerformance={handleUpdatePerformance}
        />
      )}

      {editingConstraint && (
        <ConstraintEditModal
          constraint={editingConstraint.constraint}
          constraintIndex={editingConstraint.index}
          onClose={() => setEditingConstraint(null)}
          onUpdate={handleUpdateConstraint}
          onDelete={handleDeleteConstraint}
        />
      )}


      {/* User Profile Modal */}
      <UserProfileModal
        isOpen={isVibeOpen}
        onClose={() => setIsVibeOpen(false)}
        userSettings={userSettings}
        setUserSettings={setUserSettings}
        onSave={handleSaveProfile}
      />

    </div>
  );
}

export default App;
