import React, { useState, useEffect } from 'react';

export default function TaskEditModal({ task, onClose, onUpdateTask, onUpdatePerformance }) {
    // Helper to convert decimal hour (e.g. 14.5) to "HH:MM"
    const toTimeString = (dec) => {
        const h = Math.floor(dec);
        const m = Math.round((dec - h) * 60);
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
    };

    // Helper to convert "HH:MM" back to decimal hour
    const toDecimalHour = (timeStr) => {
        if (!timeStr) return 0;
        const [h, m] = timeStr.split(':').map(Number);
        return h + (m / 60);
    };

    const [duration, setDuration] = useState(task.duration || task.duration_mins || 0);
    const [startTime, setStartTime] = useState(toTimeString(task.scheduled_start || 0));
    const [day, setDay] = useState(task.scheduled_day || 'Sun');
    const [isCompleted, setIsCompleted] = useState(task.status === 'completed');

    // Initialize states from existing task data if available
    const [percentageScore, setPercentageScore] = useState(task.reportData?.percentageScore || '');
    const [rawCount, setRawCount] = useState(task.reportData?.rawCount || '');

    // Simulation-specific state
    const [simChapters, setSimChapters] = useState(task.reportData?.simChapters || {
        q1: '', q2: '',
        v1: '', v2: '',
        e1: '', e2: ''
    });
    const [pilots, setPilots] = useState(task.reportData?.pilots || []); // { type, score }

    const DENOMINATORS = {
        'Quantitative': 20,
        'English': 22,
        'Verbal': 23,
        'Essay': 100
    };

    const name = (task.name || "").toLowerCase();
    const tag = (task.tag || "").toLowerCase();

    // Determine Reporting Type
    const isSim = name.includes("simulation");
    const isTimed = name.includes("timed section");
    const isSubject = ["quantitative", "verbal", "english", "essay"].includes(tag);

    const getTimedCategory = () => {
        if (name.includes("quant")) return "Quantitative";
        if (name.includes("verbal")) return "Verbal";
        if (name.includes("english")) return "English";
        return null;
    };

    const handleSave = (e) => {
        e.preventDefault();

        // Prepare report data for persistence
        const reportData = {
            percentageScore,
            rawCount,
            simChapters,
            pilots
        };

        // 1. Update Task Timing/Status AND Persist ReportData
        onUpdateTask(task.id, {
            duration: parseInt(duration),
            scheduled_start: toDecimalHour(startTime),
            scheduled_day: day,
            status: isCompleted ? 'completed' : 'scheduled',
            reportData // Save the results back to the task itself
        });

        // 2. Handle Global Performance Update
        if (isSim) {
            const results = {
                'Quantitative': [simChapters.q1, simChapters.q2],
                'Verbal': [simChapters.v1, simChapters.v2],
                'English': [simChapters.e1, simChapters.e2]
            };
            // Add Pilots
            pilots.forEach(p => {
                if (results[p.type]) results[p.type].push(p.score);
            });

            // Calculate & Update for each subject
            Object.keys(results).forEach(cat => {
                const validScores = results[cat].filter(s => s !== '');
                if (validScores.length > 0) {
                    const totalCorrect = validScores.reduce((sum, s) => sum + parseInt(s), 0);
                    const totalQuestions = validScores.length * DENOMINATORS[cat];
                    onUpdatePerformance(cat, (totalCorrect / totalQuestions) * 100, null);
                }
            });
        } else if (isTimed) {
            const cat = getTimedCategory();
            if (cat && rawCount !== '') {
                onUpdatePerformance(cat, (parseInt(rawCount) / DENOMINATORS[cat]) * 100, null);
            }
        } else if (isSubject && percentageScore !== '') {
            const cat = tag.charAt(0).toUpperCase() + tag.slice(1);
            onUpdatePerformance(cat, parseFloat(percentageScore), null);
        }

        onClose();
    };

    const addPilot = () => {
        setPilots([...pilots, { type: 'Quantitative', score: '' }]);
    };

    const updatePilot = (idx, field, val) => {
        const newPilots = [...pilots];
        newPilots[idx][field] = val;
        setPilots(newPilots);
    };

    const removePilot = (idx) => {
        setPilots(pilots.filter((_, i) => i !== idx));
    };

    return (
        <div className="report-modal-overlay">
            <div className="report-modal" style={{ width: isSim ? '600px' : '420px', maxHeight: '90vh', overflowY: 'auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, color: 'var(--color-primary)', fontSize: '1.2rem' }}>
                        {isSim ? '🏟️ Simulation Report' : isTimed ? '⏱️ Timed Section' : '📝 Edit Task'}
                    </h3>
                    <button onClick={onClose} style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '1.5rem', color: '#94a3b8' }}>×</button>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid #f1f5f9' }}>
                    <div>
                        <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#0f172a', marginBottom: '4px' }}>{task.name || task.title}</div>
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Category: {task.tag}</div>
                    </div>
                    <button
                        type="button"
                        onClick={() => setIsCompleted(!isCompleted)}
                        style={{
                            background: isCompleted ? '#10b981' : '#f1f5f9',
                            color: isCompleted ? 'white' : '#64748b',
                            border: 'none', padding: '6px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700,
                            cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '4px'
                        }}
                    >
                        {isCompleted ? '✅ DONE' : '⭕ MARK DONE'}
                    </button>
                </div>

                <form onSubmit={handleSave}>
                    {/* Basic Scheduling */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>Day</label>
                            <select value={day} onChange={(e) => setDay(e.target.value)} className="modal-input">
                                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Start (HH:MM)</label>
                            <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} className="modal-input" style={{ width: '100%' }} />
                        </div>
                        <div className="form-group" style={{ gridColumn: 'span 2' }}>
                            <label>Duration (Minutes)</label>
                            <input type="number" value={duration} onChange={(e) => setDuration(e.target.value)} className="modal-input" />
                        </div>
                    </div>

                    {/* Specialized Reporting UI */}
                    <div style={{ marginTop: '2rem', padding: '1.25rem', background: '#f8fafc', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                        <h4 style={{ margin: '0 0 1rem 0', fontSize: '0.9rem', color: '#475569', fontWeight: 700 }}>
                            {isSim ? "REPORT SIMULATION RESULTS" : "REPORT RESULTS"}
                        </h4>

                        {isSim && (
                            <div className="simulation-reporting slide-in">
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                                    <div>
                                        <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>QUANT CHAPTERS (20q)</label>
                                        <div style={{ display: 'flex', gap: '5px' }}>
                                            <input type="number" placeholder="Q1" value={simChapters.q1} onChange={(e) => setSimChapters({ ...simChapters, q1: e.target.value })} className="modal-input" />
                                            <input type="number" placeholder="Q2" value={simChapters.q2} onChange={(e) => setSimChapters({ ...simChapters, q2: e.target.value })} className="modal-input" />
                                        </div>
                                    </div>
                                    <div>
                                        <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>VERBAL CHAPTERS (23q)</label>
                                        <div style={{ display: 'flex', gap: '5px' }}>
                                            <input type="number" placeholder="V1" value={simChapters.v1} onChange={(e) => setSimChapters({ ...simChapters, v1: e.target.value })} className="modal-input" />
                                            <input type="number" placeholder="V2" value={simChapters.v2} onChange={(e) => setSimChapters({ ...simChapters, v2: e.target.value })} className="modal-input" />
                                        </div>
                                    </div>
                                    <div style={{ gridColumn: 'span 2' }}>
                                        <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>ENGLISH CHAPTERS (22q)</label>
                                        <div style={{ display: 'flex', gap: '5px' }}>
                                            <input type="number" placeholder="E1" value={simChapters.e1} onChange={(e) => setSimChapters({ ...simChapters, e1: e.target.value })} className="modal-input" />
                                            <input type="number" placeholder="E2" value={simChapters.e2} onChange={(e) => setSimChapters({ ...simChapters, e2: e.target.value })} className="modal-input" />
                                        </div>
                                    </div>
                                </div>

                                <div style={{ marginTop: '1.5rem', borderTop: '1px dashed #e2e8f0', paddingTop: '1rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>PILOT CHAPTERS</label>
                                        <button type="button" onClick={addPilot} style={{ background: 'none', border: 'none', color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer' }}>+ Add Pilot</button>
                                    </div>
                                    {pilots.map((p, idx) => (
                                        <div key={idx} style={{ display: 'flex', gap: '8px', marginTop: '8px', alignItems: 'center' }}>
                                            <select value={p.type} onChange={(e) => updatePilot(idx, 'type', e.target.value)} className="modal-input" style={{ flex: 1.5, fontSize: '0.8rem' }}>
                                                <option value="Quantitative">Quant</option>
                                                <option value="Verbal">Verbal</option>
                                                <option value="English">English</option>
                                            </select>
                                            <input type="number" placeholder="Score" value={p.score} onChange={(e) => updatePilot(idx, 'score', e.target.value)} className="modal-input" style={{ flex: 1 }} />
                                            <button type="button" onClick={() => removePilot(idx)} style={{ border: 'none', background: '#fee2e2', color: '#ef4444', borderRadius: '8px', padding: '8px' }}>✕</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {isTimed && !isSim && (
                            <div className="timed-reporting slide-in">
                                <label style={{ fontSize: '0.8rem', color: '#64748b' }}>Correct Answers (out of {DENOMINATORS[getTimedCategory()] || '--'})</label>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: '10px' }}>
                                    <input
                                        type="number" step="1" min="0"
                                        max={DENOMINATORS[getTimedCategory()]}
                                        value={rawCount}
                                        onChange={(e) => setRawCount(e.target.value)}
                                        className="modal-input" style={{ width: '100px', fontSize: '1.5rem', fontWeight: 700, textAlign: 'center' }}
                                    />
                                    <div style={{ fontSize: '1.2rem', color: '#94a3b8' }}>/ {DENOMINATORS[getTimedCategory()]}</div>
                                </div>
                            </div>
                        )}

                        {isSubject && !isTimed && !isSim && (
                            <div className="percentage-reporting slide-in">
                                <label style={{ fontSize: '0.8rem', color: '#64748b' }}>Success Percentage (0-100%)</label>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
                                    <input
                                        type="number" min="0" max="100"
                                        value={percentageScore}
                                        onChange={(e) => setPercentageScore(e.target.value)}
                                        className="modal-input" style={{ width: '100px', fontSize: '1.2rem', fontWeight: 700 }}
                                    />
                                    <span style={{ fontSize: '1.2rem', color: '#94a3b8' }}>%</span>
                                </div>
                            </div>
                        )}

                        {!isSim && !isTimed && !isSubject && (
                            <div style={{ fontSize: '0.85rem', color: '#94a3b8', fontStyle: 'italic' }}>
                                This task doesn't require score reporting.
                            </div>
                        )}
                    </div>

                    <div style={{ display: 'flex', gap: '12px', marginTop: '2rem' }}>
                        <button type="button" onClick={onClose} className="btn-secondary" style={{ flex: 1 }}>Discard</button>
                        <button type="submit" className="modal-submit-btn" style={{ flex: 2 }}>Update & Save Results</button>
                    </div>
                </form>
            </div>
        </div>
    );
}
