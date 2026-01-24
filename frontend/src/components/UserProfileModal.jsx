import React from 'react';

const UserProfileModal = ({
    isOpen,
    onClose,
    userSettings,
    setUserSettings,
    userProfile,
    setUserProfile,
    onSave
}) => {
    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
            <div className="glass-panel" style={{
                backgroundColor: 'white', padding: '2rem', borderRadius: '24px',
                width: '650px', maxWidth: '95%', maxHeight: '90vh', overflowY: 'auto',
                boxShadow: '0 20px 50px rgba(0,0,0,0.2)', border: 'none'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                            width: '50px', height: '50px', background: 'var(--color-primary-soft)',
                            borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '1.5rem'
                        }}>👤</div>
                        <div>
                            <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#0f172a' }}>Personal Profile</h2>
                            <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748b' }}>Customize your AI learning experience</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        style={{ background: 'none', border: 'none', fontSize: '1.8rem', cursor: 'pointer', color: '#94a3b8' }}
                    >×</button>
                </div>

                <div className="profile-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div className="form-group">
                        <label>Display Name</label>
                        <input
                            type="text" className="modal-input" placeholder="Your name"
                            value={userSettings.username || ''}
                            onChange={(e) => setUserSettings({ ...userSettings, username: e.target.value })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Target Score</label>
                        <input
                            type="number" className="modal-input" placeholder="e.g. 700"
                            value={userSettings.target_score || ''}
                            onChange={(e) => setUserSettings({ ...userSettings, target_score: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label>Peak Energy Time</label>
                        <select
                            className="modal-input"
                            value={userSettings.peak_energy || 'morning'}
                            onChange={(e) => setUserSettings({ ...userSettings, peak_energy: e.target.value })}
                        >
                            <option value="morning">☀️ Morning Person</option>
                            <option value="afternoon">🌤️ Afternoon Person</option>
                            <option value="evening">🌙 Evening Person</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Scheduling Style</label>
                        <select
                            className="modal-input"
                            value={userSettings.scheduling_style || 'spread'}
                            onChange={(e) => setUserSettings({ ...userSettings, scheduling_style: e.target.value })}
                        >
                            <option value="spread">📅 Spread consistently</option>
                            <option value="batch">📦 Batch tasks together</option>
                        </select>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', padding: '20px', background: '#f8fafc', borderRadius: '16px', marginBottom: '20px' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, marginBottom: '6px', color: '#64748b' }}>STUDY START</label>
                        <input type="number" min="0" max="23" className="modal-input" value={userSettings.study_start} onChange={(e) => setUserSettings({ ...userSettings, study_start: parseInt(e.target.value) })} />
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, marginBottom: '6px', color: '#64748b' }}>STUDY END</label>
                        <input type="number" min="0" max="23" className="modal-input" value={userSettings.study_end} onChange={(e) => setUserSettings({ ...userSettings, study_end: parseInt(e.target.value) })} />
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, marginBottom: '6px', color: '#64748b' }}>DAILY LIMIT</label>
                        <input type="number" min="1" max="16" className="modal-input" value={userSettings.max_daily_hours} onChange={(e) => setUserSettings({ ...userSettings, max_daily_hours: parseInt(e.target.value) })} />
                    </div>
                </div>

                <div className="form-group">
                    <label>Additional Notes & Preferences</label>
                    <textarea
                        value={userProfile}
                        onChange={(e) => setUserProfile(e.target.value)}
                        style={{
                            width: '100%', height: '120px', padding: '15px', borderRadius: '12px',
                            border: '2px solid #edf2f7', fontSize: '0.95rem', outline: 'none', resize: 'none'
                        }}
                        placeholder="Anything else the AI should know?"
                    />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '2.5rem' }}>
                    <button className="btn-secondary" onClick={onClose} style={{ padding: '12px 24px', borderRadius: '12px' }}>Cancel</button>
                    <button className="btn-primary" onClick={onSave} style={{ padding: '12px 30px', borderRadius: '12px', background: 'var(--color-primary)' }}>Save Profile</button>
                </div>
            </div>
        </div>
    );
};

export default UserProfileModal;
