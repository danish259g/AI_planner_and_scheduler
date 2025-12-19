import React, { useState } from 'react';

export default function TaskBank({ tasks, onDeleteTask, onOrchestrate }) {

    const handleDragStart = (e, id) => {
        // In a real app, set drag data
        e.dataTransfer.setData('taskId', id);
    };

    return (
        <div className="task-bank-content">
            <div className="task-grid">
                {tasks.map(task => (
                    <div
                        key={task.id}
                        className="task-chip"
                        draggable
                        onDragStart={(e) => handleDragStart(e, task.id)}
                        title={`Tag: ${task.tag}`}
                    >
                        <span className="task-chip-title">{task.title}</span>
                        <span className="task-chip-time">{task.duration_mins}m</span>
                        <button
                            className="chip-delete-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDeleteTask(task.id);
                            }}
                        >
                            ×
                        </button>
                    </div>
                ))}
            </div>

            <div className="orchestrate-container">
                <button
                    className="orchestrate-btn"
                    onClick={onOrchestrate}
                >
                    <span className="sparkle">✨</span> Orchestrate Week
                </button>
            </div>
        </div>
    );
}
