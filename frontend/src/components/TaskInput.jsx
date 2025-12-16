import React, { useState } from 'react';

export default function TaskInput({ onTaskInterpreted }) {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        setLoading(true);
        try {
            const response = await fetch('/api/interpret', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ raw_text: input }),
            });
            const data = await response.json();
            console.log('Interpreted Task:', data);
            onTaskInterpreted(data); // Pass data up
            setInput('');
        } catch (error) {
            console.error('Error interpreting task:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="task-input-container">
            <h2>Add New Task</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="e.g., Buy groceries and go for a run..."
                    disabled={loading}
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Processing...' : 'Add'}
                </button>
            </form>
        </div>
    );
}
