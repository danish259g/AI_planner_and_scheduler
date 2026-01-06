import React, { useEffect, useState } from 'react';

export default function CalendarView({ tasks, onTaskMove }) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const startHour = 7;
    const endHour = 23; // 7am to 11pm
    const hours = Array.from({ length: endHour - startHour + 1 }, (_, i) => startHour + i);

    const getTasksForSlot = (day, hour) => {
        if (!tasks) return [];
        // Match integer part of start time for the hour slot
        return tasks.filter(t => t.scheduled_day === day && Math.floor(t.scheduled_start) === hour);
    };

    const getTaskStyle = (tag) => {
        const t = (tag || '').toLowerCase();

        if (t.includes('class') || t.includes('course')) return { bg: 'var(--tag-bg-class)', border: 'var(--tag-border-class)' };
        if (t.includes('quant') || t.includes('math') || t.includes('geometry') || t.includes('algebra')) return { bg: 'var(--tag-bg-quantitative)', border: 'var(--tag-border-quantitative)' };
        if (t.includes('verbal') || t.includes('analogies') || t.includes('critical')) return { bg: 'var(--tag-bg-verbal)', border: 'var(--tag-border-verbal)' };
        if (t.includes('english') || t.includes('vocab')) return { bg: 'var(--tag-bg-english)', border: 'var(--tag-border-english)' };
        if (t.includes('sim')) return { bg: 'var(--tag-bg-simulation)', border: 'var(--tag-border-simulation)' };
        if (t.includes('essay')) return { bg: 'var(--tag-bg-essay)', border: 'var(--tag-border-essay)' };

        return { bg: 'var(--tag-bg-general)', border: 'var(--tag-border-general)' };
    };

    const handleDragStart = (e, taskId) => {
        e.dataTransfer.setData("taskId", taskId);
    };

    const handleDragOver = (e) => {
        e.preventDefault(); // Essential to allow dropping
    };

    const handleDrop = (e, day, hour) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData("taskId");
        // Convert string ID to number if needed, match backend ID type
        // Actually our IDs are numbers (timestamps), but getData returns string
        if (taskId && onTaskMove) {
            // Find task to check if ID is number or string
            onTaskMove(Number(taskId), day, hour);
        }
    };

    return (
        <div className="calendar-grid">
            {/* Header Row */}
            <div className="grid-corner"></div>
            {days.map(day => (
                <div key={day} className="grid-header-cell">{day}</div>
            ))}

            {/* Time Rows */}
            {hours.map(hour => (
                <React.Fragment key={hour}>
                    <div className="grid-time-cell">
                        {hour}:00
                    </div>
                    {days.map(day => {
                        const cellTasks = getTasksForSlot(day, hour);
                        return (
                            <div
                                key={`${day}-${hour}`}
                                className="grid-cell"
                                onDragOver={handleDragOver}
                                onDrop={(e) => handleDrop(e, day, hour)}
                            >
                                {cellTasks.map(task => {
                                    // 1 hour = 3rem.
                                    // Height = (duration / 60) * 3rem.
                                    // Subtract a small margin for spacing.
                                    const duration = task.duration || task.duration_mins;
                                    const heightRem = (duration / 60) * 3;
                                    const tag = task.tag || 'General';

                                    const styleInfo = getTaskStyle(tag);

                                    return (
                                        <div
                                            key={task.id}
                                            className="calendar-task"
                                            draggable
                                            onDragStart={(e) => handleDragStart(e, task.id)}
                                            title={`${task.name || task.title} (${duration}m)`}
                                            style={{
                                                height: `${heightRem}rem`,
                                                position: 'absolute',
                                                top: 0,
                                                left: 0,
                                                right: 0,
                                                marginBottom: '1px',
                                                zIndex: 10,
                                                backgroundColor: styleInfo.bg,
                                                borderLeft: `3px solid ${styleInfo.border}`,
                                                color: '#333',
                                                fontSize: '0.75rem',
                                                padding: '2px 4px',
                                                overflow: 'hidden',
                                                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                                                cursor: 'move'
                                            }}
                                        >
                                            <div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {task.name || task.title}
                                            </div>
                                            {task.location && task.location !== 'Unknown' && task.location !== 'Home' && (
                                                <div style={{ fontSize: '0.7rem', opacity: 0.8, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                    📍 {task.location}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        );
                    })}
                </React.Fragment>
            ))}
        </div>
    );
}
