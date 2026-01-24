import React, { useEffect, useState } from 'react';

export default function CalendarView({ tasks, userSettings, onTaskMove, onTaskUpdate, onTaskClick, onConstraintClick }) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const startHour = 7;
    const endHour = 23; // 7am to 11pm
    const hours = Array.from({ length: endHour - startHour + 1 }, (_, i) => startHour + i);

    const formatTime = (decimalHour) => {
        const h = Math.floor(decimalHour);
        const m = Math.round((decimalHour - h) * 60);
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
    };

    const getItemsForSlot = (day, hour) => {
        const allItems = [];

        // Add Study Tasks
        if (tasks) {
            tasks.filter(t => {
                if (!t.scheduled_day) return false;
                // Match "Tue" with "Tuesday" or "Tue"
                const taskDayStr = String(t.scheduled_day);
                const dayMatches = taskDayStr.toLowerCase().startsWith(day.toLowerCase());
                return dayMatches && Math.floor(t.scheduled_start) === hour;
            }).forEach(t => allItems.push({ ...t, type: 'task' }));
        }

        // Add Constraints
        if (userSettings?.constraints) {
            userSettings.constraints.filter(c => c.day === day && Math.floor(c.start) === hour)
                .forEach(c => allItems.push({ ...c, type: 'constraint' }));
        }

        return allItems;
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
        e.preventDefault();
    };

    const handleDrop = (e, day, hour) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData("taskId");
        if (taskId && onTaskMove) {
            onTaskMove(taskId, day, hour);
        }
    };

    const handleTaskClick = (task) => {
        if (onTaskClick) onTaskClick(task);
    };

    return (
        <div className="calendar-grid">
            <div className="grid-corner"></div>
            {days.map(day => (
                <div key={day} className="grid-header-cell">{day}</div>
            ))}

            {hours.map(hour => (
                <React.Fragment key={hour}>
                    <div className="grid-time-cell">
                        {hour}:00
                    </div>
                    {days.map(day => {
                        const items = getItemsForSlot(day, hour);

                        // Check if outside study window
                        const isOutsideWindow = userSettings && (hour < userSettings.study_start || hour >= userSettings.study_end);

                        return (
                            <div
                                key={`${day}-${hour}`}
                                className={`grid-cell ${isOutsideWindow ? 'outside-window' : ''}`}
                                onDragOver={handleDragOver}
                                onDrop={(e) => handleDrop(e, day, hour)}
                            >
                                {items.map((item, idx) => {
                                    if (item.type === 'constraint') {
                                        const duration = (item.end - item.start) * 60;
                                        return (
                                            <div
                                                key={`const-${idx}`}
                                                className="calendar-task constraint-block"
                                                onClick={(e) => { e.stopPropagation(); onConstraintClick && onConstraintClick(item, idx); }}
                                                style={{
                                                    height: `${(duration / 60) * 3}rem`,
                                                    position: 'absolute',
                                                    top: `${(item.start % 1) * 3}rem`,
                                                    left: 0, right: 0, zIndex: 5,
                                                    backgroundColor: '#f1f5f9',
                                                    borderLeft: '4px solid #94a3b8',
                                                    color: '#475569',
                                                    fontSize: '0.7rem',
                                                    padding: '4px 8px',
                                                    fontWeight: 700,
                                                    boxShadow: 'inset 0 0 0 1px rgba(0,0,0,0.05)',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                    <span>🔒</span> {item.name}
                                                </div>
                                                <div style={{ fontSize: '0.6rem', opacity: 0.7 }}>
                                                    {item.start}:00 - {item.end}:00
                                                </div>
                                            </div>
                                        );
                                    }

                                    // Render Task
                                    const duration = item.duration || item.duration_mins;
                                    const heightRem = (duration / 60) * 3;
                                    const tag = item.tag || 'General';
                                    const styleInfo = getTaskStyle(tag);
                                    const timeRange = `${formatTime(item.scheduled_start)} - ${formatTime(item.scheduled_start + (duration / 60))}`;

                                    const handleUnschedule = (e) => {
                                        e.stopPropagation();
                                        onTaskUpdate(item.id, {
                                            scheduled_day: null,
                                            scheduled_start: null,
                                            scheduled_end: null,
                                            status: 'pending'
                                        });
                                    };

                                    const isDone = item.status === 'completed';

                                    return (
                                        <div
                                            key={item.id}
                                            className={`calendar-task ${isDone ? 'task-done' : ''}`}
                                            draggable
                                            onDragStart={(e) => handleDragStart(e, item.id)}
                                            onClick={() => handleTaskClick(item)}
                                            title={`${item.name || item.title}\nTime: ${timeRange}\nDuration: ${duration}m\nStatus: ${item.status || 'pending'}`}
                                            style={{
                                                height: `${heightRem}rem`,
                                                position: 'absolute',
                                                top: `${(item.scheduled_start % 1) * 3}rem`,
                                                left: 0, right: 0, zIndex: 10,
                                                backgroundColor: styleInfo.bg,
                                                borderLeft: `3px solid ${styleInfo.border}`,
                                                color: '#333',
                                                fontSize: duration <= 45 ? '0.7rem' : '0.75rem',
                                                padding: '1px 4px',
                                                overflow: 'hidden',
                                                lineHeight: 1.1,
                                                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                                                cursor: 'pointer',
                                                opacity: isDone ? 0.6 : 1,
                                                filter: isDone ? 'grayscale(0.2)' : 'none'
                                            }}
                                        >
                                            <button
                                                onClick={handleUnschedule}
                                                style={{
                                                    position: 'absolute', top: '2px', right: '2px',
                                                    background: 'rgba(255,255,255,0.5)', border: 'none',
                                                    borderRadius: '4px', width: '18px', height: '18px',
                                                    cursor: 'pointer', fontSize: '10px', display: 'flex',
                                                    alignItems: 'center', justifyContent: 'center', zIndex: 11
                                                }}
                                                title="Return to Bank"
                                            >↩</button>
                                            <div style={{
                                                fontWeight: 600,
                                                whiteSpace: 'nowrap',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                paddingRight: '18px',
                                                textDecoration: isDone ? 'line-through' : 'none'
                                            }}>
                                                {isDone && '✅ '}{item.name || item.title}
                                            </div>
                                            <div style={{ fontSize: '0.65rem', opacity: 0.7 }}>
                                                {timeRange}
                                            </div>
                                            {item.location && item.location !== 'Unknown' && item.location !== 'Home' && (
                                                <div style={{ fontSize: '0.7rem', opacity: 0.8, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                    📍 {item.location}
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
            <style>{`
                .outside-window {
                    background-color: #f1f5f9 !important;
                    background-image: repeating-linear-gradient(
                        45deg, 
                        transparent, 
                        transparent 15px, 
                        rgba(148, 163, 184, 0.12) 15px, 
                        rgba(148, 163, 184, 0.12) 30px
                    ) !important;
                    border-color: #e2e8f0 !important;
                }
                .grid-cell.outside-window:hover {
                    background-color: #e2e8f0 !important;
                }
                .constraint-block:hover {
                    filter: brightness(0.95);
                }
            `}</style>
        </div>
    );
}
