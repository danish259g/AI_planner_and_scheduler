import React, { useState } from 'react';

export default function TaskInput({ onTaskInterpreted }) {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        setLoading(true);
        try {
            // Call the real backend
            const response = await fetch('http://127.0.0.1:8000/api/interpret', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ raw_text: input })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            console.log('Interpreted Task:', data);

            onTaskInterpreted && onTaskInterpreted(data);
            setInput('');
        } catch (error) {
            console.error('Error interpreting task:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form className="task-input-form" onSubmit={handleSubmit}>
            <input
                type="text"
                className="premium-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="What do you need to get done?"
                disabled={loading}
            />
            <button type="submit" className="icon-btn" disabled={loading}>
                {loading ? '...' : '→'}
            </button>
        </form>
    );
}
