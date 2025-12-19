import React, { useState } from 'react';

export default function TaskInput({ onTaskInterpreted }) {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        setLoading(true);
        try {
            // Simulate API call for now or use real endpoint if server is up
            // const response = await fetch('/api/interpret', ...);
            // const data = await response.json();

            // Mock response for UI testing
            const mockData = { title: input, duration: 60 };

            console.log('Interpreted Task:', mockData);
            onTaskInterpreted && onTaskInterpreted(mockData);
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
