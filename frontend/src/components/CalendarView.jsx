import React, { useEffect, useState } from 'react';

export default function CalendarView({ tasks }) {
    const [schedule, setSchedule] = useState(null);
    const [loading, setLoading] = useState(false);

    // Constants for grid
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const startHour = 8; // 8 AM
    const endHour = 22; // 10 PM
    const hours = Array.from({ length: endHour - startHour + 1 }, (_, i) => startHour + i);

    // Auto-generate schedule when tasks change (for demo purposes)
    useEffect(() => {
        if (tasks.length > 0) {
            generateSchedule();
        }
    }, [tasks]);

    const generateSchedule = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/schedule/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tasks),
            });
            const data = await response.json();
            setSchedule(data);
        } catch (error) {
            console.error('Error generating schedule:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="calendar-view">
            <div className="calendar-header">
                <h2>Weekly Schedule</h2>
                {loading && <span className="loading-badge">Optimization in progress...</span>}
            </div>

            <div className="calendar-grid">
                {/* Time Column Header */}
                <div className="grid-cell time-header-cell"></div>

                {/* Day Headers */}
                {days.map(day => (
                    <div key={day} className="grid-cell day-header">{day}</div>
                ))}

                {/* Grid Rows */}
                {hours.map(hour => (
                    <React.Fragment key={hour}>
                        <div className="grid-cell time-slot">
                            {hour}:00
                        </div>
                        {days.map(day => (
                            <div key={`${day}-${hour}`} className="grid-cell day-slot">
                                {/* 
                            In a real app, we would map the 'schedule' events here. 
                            For this dummy skeleton, we just leave them empty or show a placeholder 
                            if a scheduled item matches.
                        */}
                            </div>
                        ))}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
}
