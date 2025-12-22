import React, { useEffect, useState } from 'react';

export default function CalendarView({ tasks }) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const startHour = 8;
    const endHour = 20; // Shortened for clearer view
    const hours = Array.from({ length: endHour - startHour + 1 }, (_, i) => startHour + i);

    const getTasksForSlot = (day, hour) => {
        if (!tasks) return [];
        return tasks.filter(t => t.scheduled_day === day && t.scheduled_hour === hour);
    };

    const getTagColor = (tag) => {
        const colors = {
            'Work': '#e3f2fd', // Light Blue
            'Personal': '#e8f5e9', // Light Green
            'Health': '#ffebee', // Light Red
            'Study': '#f3e5f5', // Light Purple
            'Errand': '#fff3e0', // Light Orange
            'Home': '#f5f5f5'    // Grey
        };
        return colors[tag] || '#e3f2fd'; // Default to blue-ish
    };

    const getTagBorderColor = (tag) => {
        const colors = {
            'Work': '#2196f3',
            'Personal': '#4caf50',
            'Health': '#f44336',
            'Study': '#9c27b0',
            'Errand': '#ff9800',
            'Home': '#9e9e9e'
        };
        return colors[tag] || '#2196f3';
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
                            <div key={`${day}-${hour}`} className="grid-cell">
                                {cellTasks.map(task => {
                                    // 1 hour = 3rem.
                                    // Height = (duration / 60) * 3rem.
                                    // Subtract a small margin for spacing.
                                    const duration = task.duration || task.duration_mins;
                                    const heightRem = (duration / 60) * 3;
                                    const tag = task.tag || 'General';

                                    return (
                                        <div
                                            key={task.id}
                                            className="calendar-task"
                                            title={`${task.name || task.title} (${duration}m)`}
                                            style={{
                                                height: `${heightRem}rem`,
                                                position: 'absolute',
                                                top: 0,
                                                left: 0,
                                                right: 0,
                                                marginBottom: '1px',
                                                zIndex: 10,
                                                backgroundColor: getTagColor(tag),
                                                borderLeft: `3px solid ${getTagBorderColor(tag)}`,
                                                color: '#333',
                                                fontSize: '0.75rem',
                                                padding: '2px 4px',
                                                overflow: 'hidden',
                                                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
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
