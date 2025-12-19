import React, { useState } from 'react';

export default function TaskBank({ tasks }) {

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
                        <span className="bank-card-time">{task.duration_mins}m</span>
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
