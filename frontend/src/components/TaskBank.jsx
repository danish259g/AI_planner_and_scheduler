import React, { useState } from 'react';

export default function TaskBank({ tasks, onDeleteTask, onOrchestrate, onTaskUpdate, isOrchestrating }) {
    const [tooltip, setTooltip] = useState({ visible: false, task: null, style: {} });
    const timerRef = React.useRef(null);

    const handleDragStart = (e, id) => {
        // In a real app, set drag data
        e.dataTransfer.setData('taskId', id);
    };

    const handleMouseEnter = (e, task) => {
        const rect = e.currentTarget.getBoundingClientRect();
        // Clear any existing timer just in case
        if (timerRef.current) clearTimeout(timerRef.current);

        const viewportHeight = window.innerHeight;
        const spaceBelow = viewportHeight - rect.bottom;

        let newStyle = {
            left: rect.right + 10,
            top: rect.top
        };

        // Smart flip: if less than 350px below, flip to bottom alignment
        if (spaceBelow < 350) {
            newStyle = {
                left: rect.right + 10,
                bottom: viewportHeight - rect.bottom
            };
        }

        timerRef.current = setTimeout(() => {
            setTooltip({
                visible: true,
                task: task,
                style: newStyle
            });
        }, 500); // 500ms delay
    };

    const handleMouseLeave = () => {
        if (timerRef.current) {
            clearTimeout(timerRef.current);
            timerRef.current = null;
        }
        setTooltip({ ...tooltip, visible: false });
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
                {tasks.filter(t => t.status !== 'scheduled' && t.status !== 'completed').length === 0 ? (
                    <div style={{ padding: '20px', textAlign: 'center', color: '#888', fontStyle: 'italic', width: '100%' }}>
                        Building your bank...<br />
                        (or everything is planned! 🎉)
                    </div>
                ) : (
                    tasks.filter(t => t.status !== 'scheduled' && t.status !== 'completed').map(task => (
                        <div
                            key={task.id}
                            className="task-chip"
                            draggable
                            onDragStart={(e) => handleDragStart(e, task.id)}
                            onMouseEnter={(e) => handleMouseEnter(e, task)}
                            onMouseLeave={handleMouseLeave}
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
                                    const hour = window.prompt("Enter Start Hour (0-23):", "10");
                                    if (!hour) return;

                                    onTaskUpdate(task.id, {
                                        scheduled_day: day,
                                        scheduled_start: parseFloat(hour),
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

            {/* Fixed Tooltip Portal */}
            {tooltip.visible && tooltip.task && (
                <div
                    className="task-tooltip-fixed"
                    style={{
                        position: 'fixed',
                        zIndex: 9999,
                        ...tooltip.style
                    }}
                >
                    <strong>{tooltip.task.name || tooltip.task.title}</strong>
                    <div className="tooltip-row"><span>⏱️ Duration:</span> {tooltip.task.duration || tooltip.task.duration_mins}m</div>
                    <div className="tooltip-row"><span>🏷️ Tag:</span> {tooltip.task.tag || 'General'}</div>
                    <div className="tooltip-row"><span>📍 Location:</span> {tooltip.task.location || 'Home'}</div>
                    <div className="tooltip-row"><span>🔥 Priority:</span> {tooltip.task.priority || 'Medium'}</div>
                    {tooltip.task.day && <div className="tooltip-row"><span>📅 Day:</span> {tooltip.task.day}</div>}
                    {(tooltip.task.start_time || tooltip.task.end_time) && (
                        <div className="tooltip-row"><span>⏰ Time:</span> {tooltip.task.start_time || '?'} - {tooltip.task.end_time || '?'}</div>
                    )}
                    {tooltip.task.is_locked && <div className="tooltip-row"><span>🔒 Locked:</span> Yes</div>}
                    {tooltip.task.comments && <div className="tooltip-row"><span>📝 Note:</span> {tooltip.task.comments}</div>}
                </div>
            )}
        </div>
    );
}
