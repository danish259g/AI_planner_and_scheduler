import React, { useState } from 'react';

export default function ConstraintEditModal({ constraint, constraintIndex, onClose, onUpdate, onDelete }) {
    const [name, setName] = useState(constraint.name);
    const [day, setDay] = useState(constraint.day);
    const [start, setStart] = useState(constraint.start);
    const [end, setEnd] = useState(constraint.end);

    const handleSave = (e) => {
        e.preventDefault();
        onUpdate(constraintIndex, {
            name,
            day,
            start: parseInt(start),
            end: parseInt(end)
        });
        onClose();
    };

    const handleDelete = () => {
        if (window.confirm("Are you sure you want to delete this constraint?")) {
            onDelete(constraintIndex);
            onClose();
        }
    };

    return (
        <div className="report-modal-overlay">
            <div className="report-modal" style={{ width: '400px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, color: 'var(--color-primary)', fontSize: '1.2rem' }}>
                        🔒 Edit Constraint
                    </h3>
                    <button onClick={onClose} style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '1.5rem', color: '#94a3b8' }}>×</button>
                </div>

                <form onSubmit={handleSave}>
                    <div className="form-group" style={{ marginBottom: '12px' }}>
                        <label>Name</label>
                        <input
                            type="text"
                            className="modal-input"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g. Work, Gym"
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr', gap: '10px', marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>Day</label>
                            <select value={day} onChange={(e) => setDay(e.target.value)} className="modal-input">
                                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Start</label>
                            <input type="number" min="0" max="23" value={start} onChange={(e) => setStart(e.target.value)} className="modal-input" />
                        </div>
                        <div className="form-group">
                            <label>End</label>
                            <input type="number" min="0" max="23" value={end} onChange={(e) => setEnd(e.target.value)} className="modal-input" />
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '12px', marginTop: '1rem' }}>
                        <button type="button" onClick={handleDelete} className="btn-secondary" style={{ flex: 1, borderColor: '#ef4444', color: '#ef4444' }}>Delete</button>
                        <button type="submit" className="modal-submit-btn" style={{ flex: 2 }}>Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    );
}
