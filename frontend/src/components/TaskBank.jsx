import React, { useState } from 'react';

export default function TaskBank({ tasks, onDeleteTask, onOrchestrate }) {
    const [tooltip, setTooltip] = useState({ visible: false, task: null, x: 0, y: 0 });

    const handleDragStart = (e, id) => {
        // In a real app, set drag data
        e.dataTransfer.setData('taskId', id);
    };

    const handleMouseEnter = (e, task) => {
        const rect = e.currentTarget.getBoundingClientRect();
        setTooltip({
            visible: true,
            task: task,
            x: rect.right + 10, // Position to the right of the task
            y: rect.top
        });
    };

    const handleMouseLeave = () => {
        setTooltip({ ...tooltip, visible: false });
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
                        onMouseEnter={(e) => handleMouseEnter(e, task)}
                        onMouseLeave={handleMouseLeave}
                    >
                        <span className="task-chip-title">{task.name || task.title}</span>
                        <span className="task-chip-time">{task.duration || task.duration_mins}m</span>

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

            {/* Fixed Tooltip Portal */}
            {tooltip.visible && tooltip.task && (
                <div
                    className="task-tooltip-fixed"
                    style={{
                        position: 'fixed',
                        left: tooltip.x,
                        top: tooltip.y,
                        zIndex: 9999
                    }}
                >
                    <strong>{tooltip.task.name || tooltip.task.title}</strong>
                    <div className="tooltip-row"><span>⏱️ Duration:</span> {tooltip.task.duration || tooltip.task.duration_mins}m</div>
                    <div className="tooltip-row"><span>🏷️ Tag:</span> {tooltip.task.tag}</div>
                    <div className="tooltip-row"><span>📍 Location:</span> {tooltip.task.location || 'N/A'}</div>
                    <div className="tooltip-row"><span>🔥 Priority:</span> {tooltip.task.priority || 'Medium'}</div>
                    {tooltip.task.is_locked && <div className="tooltip-row"><span>🔒 Locked:</span> Yes</div>}
                    {tooltip.task.comments && <div className="tooltip-row"><span>📝 Note:</span> {tooltip.task.comments}</div>}
                </div>
            )}
        </div>
    );
}
