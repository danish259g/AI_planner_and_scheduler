import React, { useState } from 'react';

export default function TaskBank() {
    const [tasks, setTasks] = useState([
        { id: 1, title: 'Draft Q1 Report', time: '2h', tag: 'Work' },
        { id: 2, title: 'Email Marketing Team', time: '30m', tag: 'Comms' },
        { id: 3, title: 'Code Review', time: '1h', tag: 'Dev' },
        { id: 4, title: 'Gym - Leg Day', time: '1.5h', tag: 'Health' },
    ]);

    const handleDragStart = (e, id) => {
        // In a real app, set drag data
        e.dataTransfer.setData('taskId', id);
    };

    return (
        <div className="task-bank-content">
            <div className="bank-list">
                {tasks.map(task => (
                    <div
                        key={task.id}
                        className="bank-card"
                        draggable
                        onDragStart={(e) => handleDragStart(e, task.id)}
                    >
                        <div className="bank-card-header">
                            <span className="bank-card-title">{task.title}</span>
                            <span className="bank-card-tag">{task.tag}</span>
                        </div>
                        <span className="bank-card-time">{task.time}</span>
                    </div>
                ))}
            </div>

            <div className="orchestrate-container">
                <button
                    className="orchestrate-btn"
                    onClick={() => console.log('Orchestrating...')}
                >
                    <span className="sparkle">✨</span> Orchestrate Week
                </button>
            </div>
        </div>
    );
}
