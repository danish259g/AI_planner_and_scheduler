import React, { useState } from 'react';

export default function TaskInput({ onAddConstraint }) {
    // Commitment fields
    const [consName, setConsName] = useState('');
    const [consDay, setConsDay] = useState('Sun');
    const [consStart, setConsStart] = useState('');
    const [consEnd, setConsEnd] = useState('');

    const handleConsSubmit = (e) => {
        e.preventDefault();
        if (!consName || !consStart || !consEnd) return;

        onAddConstraint && onAddConstraint({
            name: consName,
            day: consDay,
            start: parseInt(consStart),
            end: parseInt(consEnd)
        });

        // Reset fields
        setConsName('');
        setConsStart('');
        setConsEnd('');
    };

    return (
        <div className="task-input-container">
            <form className="commitment-form slide-in" onSubmit={handleConsSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <input
                    placeholder="Name..."
                    className="premium-input"
                    style={{ fontSize: '0.85rem', padding: '10px 12px' }}
                    value={consName}
                    onChange={(e) => setConsName(e.target.value)}
                />
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                    <select
                        className="premium-input"
                        style={{ flex: 1.2, fontSize: '0.8rem', padding: '8px 2px', minWidth: '60px' }}
                        value={consDay}
                        onChange={(e) => setConsDay(e.target.value)}
                    >
                        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => <option key={d} value={d}>{d}</option>)}
                    </select>
                    <input
                        type="number" min="0" max="23" placeholder="Start"
                        className="premium-input"
                        style={{ flex: 1, fontSize: '0.8rem', padding: '8px 2px', minWidth: 0, textAlign: 'center' }}
                        value={consStart}
                        onChange={(e) => setConsStart(e.target.value)}
                    />
                    <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>to</span>
                    <input
                        type="number" min="0" max="23" placeholder="End"
                        className="premium-input"
                        style={{ flex: 1, fontSize: '0.8rem', padding: '8px 2px', minWidth: 0, textAlign: 'center' }}
                        value={consEnd}
                        onChange={(e) => setConsEnd(e.target.value)}
                    />
                    <button type="submit" className="icon-btn" style={{ width: '32px', height: '32px', flexShrink: 0, fontSize: '1.1rem' }}>
                        +
                    </button>
                </div>
            </form>
        </div>
    );
}
