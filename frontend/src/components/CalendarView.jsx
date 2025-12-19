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
                                    const heightRem = (task.duration_mins / 60) * 3;

                                    return (
                                        <div
                                            key={task.id}
                                            className="calendar-task"
                                            title={task.title}
                                            style={{
                                                height: `${heightRem}rem`,
                                                position: 'absolute',
                                                top: 0,
                                                left: 0,
                                                right: 0,
                                                marginBottom: '1px',
                                                zIndex: 10
                                            }}
                                        >
                                            {task.title} ({task.duration_mins}m)
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
