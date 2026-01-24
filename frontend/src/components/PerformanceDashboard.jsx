import React, { useState } from 'react';

export default function PerformanceDashboard({ performance, onUpdate, onReset }) {
    const categories = ['Quantitative', 'Verbal', 'English', 'Essay'];
    const [selectedCat, setSelectedCat] = useState(null);
    const [rawScore, setRawScore] = useState('');
    const [selfEval, setSelfEval] = useState(5);
    const [reportMode, setReportMode] = useState('result'); // 'result' or 'feeling'

    const DENOMINATORS = {
        'Quantitative': 20,
        'English': 22,
        'Verbal': 23,
        'Essay': 100
    };

    const getColor = (score, selfEval) => {
        // Handle case where one might be null (from selective updates)
        const s = score !== null ? score : 50;
        const e = selfEval !== null ? selfEval : 5;
        const combined = (s + (e * 10)) / 2;
        if (combined < 40) return '#ff6b6b'; // Red
        if (combined < 70) return '#feca57'; // Yellow/Orange
        return '#1dd1a1'; // Green
    };

    const handleUpdateClick = (cat) => {
        setSelectedCat(cat);
        setRawScore('');
        setSelfEval(performance[cat]?.self_eval || 5);
        setReportMode('result');
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (reportMode === 'result') {
            const denom = DENOMINATORS[selectedCat];
            const val = parseFloat(rawScore);
            const percentage = (val / denom) * 100;
            onUpdate(selectedCat, percentage, null);
        } else {
            onUpdate(selectedCat, null, parseInt(selfEval));
        }

        setSelectedCat(null);
    };

    return (
        <div className="performance-dashboard glass-panel" style={{ marginTop: '0.5rem', border: 'none', background: 'transparent', padding: '0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                    <span>📊</span> Performance Comparison
                </h3>
                <button
                    onClick={onReset}
                    title="Reset All Data"
                    style={{
                        background: 'none', border: '1px solid #ff6b6b44', color: '#ff6b6b',
                        padding: '4px 8px', borderRadius: '6px', fontSize: '0.7rem',
                        cursor: 'pointer', fontWeight: 600, transition: 'all 0.2s'
                    }}
                >
                    Reset
                </button>
            </div>

            {/* BAR CHART SECTION */}
            <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'space-around',
                height: '180px',
                padding: '10px 0 35px 0',
                background: 'rgba(255,255,255,0.6)',
                borderRadius: '16px',
                marginBottom: '1rem',
                border: '1px solid var(--color-border)',
                position: 'relative',
                boxShadow: '0 4px 15px rgba(0,0,0,0.03)'
            }}>
                {categories.map(cat => {
                    const data = performance[cat] || { score: 0, self_eval: 5, count: 0 };
                    const color = getColor(data.score, data.self_eval);
                    const height = Math.max(data.score || 0, 5);

                    return (
                        <div
                            key={`bar-${cat}`}
                            onClick={() => handleUpdateClick(cat)}
                            className="chart-column"
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                width: '50px',
                                height: '100%',
                                justifyContent: 'flex-end',
                                cursor: 'pointer',
                                transition: 'transform 0.2s',
                                zIndex: 2
                            }}
                        >
                            <div style={{
                                width: '24px',
                                height: `${height}%`,
                                backgroundColor: color,
                                borderRadius: '8px 8px 2px 2px',
                                transition: 'height 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                                boxShadow: `0 4px 12px ${color}55`
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                bottom: '8px',
                                fontSize: '0.65rem',
                                fontWeight: 700,
                                color: '#444',
                                textAlign: 'center',
                                width: '100%',
                                whiteSpace: 'nowrap'
                            }}>
                                {cat}
                            </div>
                        </div>
                    );
                })}
                {/* Horizontal Baseline */}
                <div style={{
                    position: 'absolute',
                    bottom: '32px',
                    left: '5%',
                    right: '5%',
                    height: '1px',
                    background: '#eee'
                }}></div>
            </div>

            {/* MODAL Overlay */}
            {selectedCat && (
                <div className="report-modal-overlay">
                    <div className="report-modal">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', alignItems: 'center' }}>
                            <h4 style={{ margin: 0, color: 'var(--color-primary)' }}>Report: {selectedCat}</h4>
                            <button onClick={() => setSelectedCat(null)} style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '1.5rem', color: '#999' }}>×</button>
                        </div>

                        {/* MODE TOGGLE */}
                        <div style={{
                            display: 'flex',
                            background: '#f1f5f9',
                            padding: '4px',
                            borderRadius: '10px',
                            marginBottom: '1.5rem'
                        }}>
                            <button
                                type="button"
                                onClick={() => setReportMode('result')}
                                style={{
                                    flex: 1, padding: '8px', border: 'none', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600,
                                    backgroundColor: reportMode === 'result' ? 'white' : 'transparent',
                                    boxShadow: reportMode === 'result' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                                    cursor: 'pointer', transition: 'all 0.2s'
                                }}
                            >
                                🎯 Test Result
                            </button>
                            <button
                                type="button"
                                onClick={() => setReportMode('feeling')}
                                style={{
                                    flex: 1, padding: '8px', border: 'none', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600,
                                    backgroundColor: reportMode === 'feeling' ? 'white' : 'transparent',
                                    boxShadow: reportMode === 'feeling' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                                    cursor: 'pointer', transition: 'all 0.2s'
                                }}
                            >
                                🧠 Feeling
                            </button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            {reportMode === 'result' ? (
                                <div className="form-group slide-in">
                                    <label>Correct Answers</label>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <input
                                            type="number"
                                            step="0.5"
                                            min="0"
                                            max={DENOMINATORS[selectedCat]}
                                            placeholder="--"
                                            value={rawScore}
                                            onChange={(e) => setRawScore(e.target.value)}
                                            className="modal-input"
                                            autoFocus
                                            required
                                        />
                                        <span style={{ fontSize: '0.9rem', color: '#666', fontWeight: 500 }}>
                                            / {DENOMINATORS[selectedCat]}
                                        </span>
                                    </div>
                                </div>
                            ) : (
                                <div className="form-group slide-in">
                                    <label>Self Assessment (Feeling)</label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={selfEval}
                                        onChange={(e) => setSelfEval(e.target.value)}
                                        style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--color-primary)' }}
                                    />
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginTop: '4px', color: '#888' }}>
                                        <span>Weak (1)</span>
                                        <span style={{ fontWeight: 'bold', color: 'var(--color-primary)', fontSize: '1.2rem' }}>{selfEval}</span>
                                        <span>Strong (10)</span>
                                    </div>
                                </div>
                            )}

                            <button type="submit" className="modal-submit-btn">
                                Save {reportMode === 'result' ? 'Result' : 'Feeling'}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.7rem', color: '#666' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ff6b6b' }}></div> Weak
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.7rem', color: '#666' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#feca57' }}></div> Average
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.7rem', color: '#666' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#1dd1a1' }}></div> Strong
                </div>
            </div>

            <p style={{ fontSize: '0.7rem', color: '#888', textAlign: 'center', marginTop: '0.5rem', fontWeight: 500 }}>
                💡 Click on a bar to report results/assessment.
            </p>

        </div>
    );
}
