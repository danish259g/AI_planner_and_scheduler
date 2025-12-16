import React, { useEffect, useState } from 'react';

export default function CalendarView({ tasks }) {
    const [schedule, setSchedule] = useState(null);
    const [loading, setLoading] = useState(false);

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
            <h2>Weekly Schedule</h2>
            {loading && <p>Optimizing schedule...</p>}

            {!loading && !schedule && <p>No schedule yet. Add tasks to begin.</p>}

            {!loading && schedule && (
                <div className="schedule-grid">
                    {/* Dummy visualization */}
                    <pre>{JSON.stringify(schedule, null, 2)}</pre>
                    <div className="week-placeholder">
                        {/* Visual blocks would go here */}
                        {schedule.tasks.map((task) => (
                            <div key={task.id} className="calendar-event">
                                <strong>{task.title}</strong>
                                <br />
                                <span>{task.duration_mins} mins</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
