import React, { useState } from 'react';

export default function NegotiationChat() {
    const [messages, setMessages] = useState([
        { sender: 'ai', message: 'Hi there! I can help you adjust your schedule.' }
    ]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { sender: 'user', message: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');

        // Mock reply
        setTimeout(() => {
            setMessages(prev => [...prev, { sender: 'ai', message: "I'll see what I can do." }]);
        }, 600);
    };

    return (
        <div className="chat-interface">
            <div className="chat-window">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.sender}`}>
                        <div className="message-bubble">
                            {msg.message}
                        </div>
                    </div>
                ))}
            </div>
            <div className="chat-input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask assistant..."
                />
            </div>
        </div>
    );
}
