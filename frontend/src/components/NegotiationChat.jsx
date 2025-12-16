import React, { useState } from 'react';

export default function NegotiationChat() {
    const [messages, setMessages] = useState([
        { sender: 'ai', message: 'Hello! I am your scheduling assistant. How can I help you tweak the plan?' }
    ]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { sender: 'user', message: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');

        try {
            const response = await fetch('/api/chat/negotiate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    history: messages
                }),
            });
            const data = await response.json();
            setMessages((prev) => [...prev, data]);
        } catch (error) {
            console.error('Error negotiating:', error);
        }
    };

    return (
        <div className="negotiation-chat">
            <h3>Assistant</h3>
            <div className="chat-window">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.sender}`}>
                        <strong>{msg.sender === 'ai' ? 'AI' : 'You'}:</strong> {msg.message}
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}
