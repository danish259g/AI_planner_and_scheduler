import React, { useState } from 'react';

export default function NegotiationChat({ messages, onSendMessage }) {
    const [input, setInput] = useState('');
    const chatEndRef = React.useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    React.useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = () => {
        if (!input.trim()) return;
        onSendMessage(input);
        setInput('');
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
                <div ref={chatEndRef} />
            </div>
            <div className="chat-input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask assistant..."
                />
            </div>
        </div>
    );
}
