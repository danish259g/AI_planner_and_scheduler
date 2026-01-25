import React, { useState } from 'react';

export default function TaskBank({ tasks, onDeleteTask, onOrchestrate, onTaskUpdate, isOrchestrating }) {


    const handleDragStart = (e, id) => {
        // In a real app, set drag data
        e.dataTransfer.setData('taskId', id);
    };



    const getTaskStyle = (tag) => {
        const t = (tag || '').toLowerCase();
        let style = { borderLeft: '4px solid', background: '' };

        if (t.includes('class') || t.includes('course') || t.includes('lesson')) {
            style.borderColor = 'var(--tag-border-class)'; style.background = 'var(--tag-bg-class)';
        } else if (t.includes('quant') || t.includes('math') || t.includes('geometry') || t.includes('algebra')) {
            style.borderColor = 'var(--tag-border-quantitative)'; style.background = 'var(--tag-bg-quantitative)';
        } else if (t.includes('verbal') || t.includes('analogies') || t.includes('critical')) {
            style.borderColor = 'var(--tag-border-verbal)'; style.background = 'var(--tag-bg-verbal)';
        } else if (t.includes('english') || t.includes('vocab')) {
            style.borderColor = 'var(--tag-border-english)'; style.background = 'var(--tag-bg-english)';
        } else if (t.includes('sim')) {
            style.borderColor = 'var(--tag-border-simulation)'; style.background = 'var(--tag-bg-simulation)';
        } else if (t.includes('essay')) {
            style.borderColor = 'var(--tag-border-essay)'; style.background = 'var(--tag-bg-essay)';
        } else {
            style.borderColor = 'var(--tag-border-general)'; style.background = 'var(--tag-bg-general)';
        }
        return style;
    };

    return (
        <div className="task-bank-content">
            <div className="task-grid">
                {tasks.filter(t => t.status !== 'scheduled' && t.status !== 'completed').length > 0 && (
                    <div style={{ width: '100%', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 700, color: '#64748b' }}>
                        UNASSIGNED TASKS
                    </div>
                )}
                {tasks.filter(t => t.status !== 'scheduled' && t.status !== 'completed').length === 0 ? (
                    <div style={{ padding: '20px', textAlign: 'center', color: '#888', fontStyle: 'italic', width: '100%' }}>
                        {tasks.length > 0 ? "All tasks scheduled! 🎉" : "Task bank is empty."}
                    </div>
                ) : (
                    tasks.filter(t => t.status !== 'scheduled' && t.status !== 'completed').map(task => (
                        <div
                            key={task.id}
                            className="task-chip"
                            draggable
                            onDragStart={(e) => handleDragStart(e, task.id)}
                            style={getTaskStyle(task.tag)}
                        >
                            <span className="task-chip-title">{task.name || task.title}</span>
                            <span className="task-chip-time">{task.duration || task.duration_mins}m</span>

                            <button
                                className="chip-schedule-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    const day = window.prompt("Enter Day (Sun, Mon, Tue, Wed, Thu, Fri, Sat):", "Sun");
                                    if (!day) return;
                                    const hourStr = window.prompt("Enter Start Hour (0-23):", "10");
                                    if (!hourStr) return;

                                    const hour = parseFloat(hourStr);
                                    if (isNaN(hour)) {
                                        alert("Invalid hour entered");
                                        return;
                                    }

                                    console.log("Scheduling task:", task.id, day, hour);

                                    onTaskUpdate(task.id, {
                                        scheduled_day: day,
                                        scheduled_start: hour,
                                        status: 'scheduled'
                                    });
                                }}
                                title="Schedule in Calendar"
                                style={{
                                    background: 'var(--color-primary)',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    marginRight: '5px',
                                    cursor: 'pointer',
                                    padding: '0 5px',
                                    fontSize: '12px',
                                    fontWeight: 'bold'
                                }}
                            >
                                +
                            </button>

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
                    ))
                )}
            </div>

            <div className="orchestrate-container">
                <button
                    className="orchestrate-btn"
                    onClick={onOrchestrate}
                    disabled={isOrchestrating}
                    style={{
                        opacity: isOrchestrating ? 0.7 : 1,
                        cursor: isOrchestrating ? 'not-allowed' : 'pointer'
                    }}
                >
                    <span className="sparkle">{isOrchestrating ? "⏳" : "✨"}</span>
                    {isOrchestrating ? "Orchestrating..." : "Orchestrate Week"}
                </button>
            </div>


        </div>
    );
}
