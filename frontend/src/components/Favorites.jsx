import React, { useState } from 'react';

const CATEGORIES = {
    "Quantitative Reasoning": {
        tag: "Quantitative",
        color: "red",
        sub: {
            "Algebra": { duration: 45 },
            "Word Problems": { duration: 45 },
            "Geometry": { duration: 45 },
            "Data Interpretation": { duration: 45 }
        }
    },
    "Verbal Reasoning": {
        tag: "Verbal",
        color: "orange",
        sub: {
            "Analogies": { duration: 30 },
            "Sentence Completions": { duration: 25 },
            "Logic & Inference": { duration: 45 },
            "Reading Comprehension": { duration: 50 },
            "Vocab Memorization": { duration: 20 },
            "Reading a Book": { duration: 30 }
        }
    },
    "English": {
        tag: "English",
        color: "blue",
        sub: {
            "Sentence Completions": { duration: 20 },
            "Restatements": { duration: 20 },
            "Reading Comprehension": { duration: 40 },
            "Vocab Memorization": { duration: 25 },
            "Reading a Book": { duration: 30 }
        }
    },
    "Essay Writing": {
        tag: "Essay",
        color: "green",
        sub: {
            "Intro & Conclusion": { duration: 30 },
            "Argumentative para": { duration: 30 },
            "Critical Thinking para": { duration: 30 },
            "Analyze Sample": { duration: 30 },
            "Full-length Essay": { duration: 35 }
        }
    },
    "Practice Modes": {
        tag: "Simulation",
        color: "purple",
        sub: {
            "Timed Section (Quant)": { duration: 20 },
            "Timed Section (Verbal)": { duration: 20 },
            "Timed Section (English)": { duration: 20 },
            "Full Simulation": { duration: 210 }
        }
    }
};

export default function Favorites({ onQuickAdd }) {
    const [path, setPath] = useState([]); // Array of keys

    // Resolve current level based on path
    let currentLevel = CATEGORIES;
    let currentTag = null;

    path.forEach(key => {
        if (currentLevel[key].tag) currentTag = currentLevel[key].tag;
        currentLevel = currentLevel[key].sub;
    });

    const handleBack = () => {
        setPath(prev => prev.slice(0, -1));
    };

    const handleSelect = (key) => {
        const target = currentLevel[key];

        // Navigate if it's a category folder
        if (target.sub) {
            setPath(prev => [...prev, key]);
        } else {
            // It's a task leaf
            onQuickAdd({
                name: key,
                duration: target.duration || 60,
                tag: currentTag || "General"
            });
        }
    };

    const renderItems = () => {
        return Object.keys(currentLevel).map(key => {
            const item = currentLevel[key];

            // ROOT LEVEL: Render Category Buttons
            if (path.length === 0) {
                return (
                    <button key={key} className="favorite-chip" onClick={() => handleSelect(key)}>
                        <span className="circle-icon" style={{ backgroundColor: item.color || "gray" }}></span>
                        {key}
                    </button>
                );
            }

            // NESTED LEVEL: Everything here is a Task we can add
            const parentColor = path.length > 0 ? CATEGORIES[path[0]]?.color : "gray";
            return (
                <button
                    key={key}
                    className="favorite-chip"
                    onClick={() => onQuickAdd({
                        name: key,
                        duration: item.duration || 60,
                        tag: currentTag || "General"
                    })}
                >
                    <span className="circle-icon" style={{ backgroundColor: parentColor }}></span>
                    {key}
                </button>
            );
        });
    };

    return (
        <div className="favorites-container">
            <div className="favorites-header" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                {path.length > 0 && (
                    <button onClick={handleBack} className="btn-back">
                        ← Back
                    </button>
                )}
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {path.length === 0 ? "Select Category" : path.join(' > ')}
                </span>
            </div>

            <div className="favorites-grid">
                {renderItems()}
            </div>

            <style>{`
                .favorites-container {
                    display: flex;
                    flex-direction: column;
                }
                .favorites-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                    gap: 8px;
                }
                .circle-icon {
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                .favorite-chip {
                    display: flex;
                    align-items: center;
                    background: white;
                    border: 1px solid var(--color-border);
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 0.85rem;
                    text-align: left;
                    cursor: pointer;
                    transition: all 0.2s;
                    color: var(--text-main);
                }
                .favorite-chip:hover {
                    border-color: var(--color-primary);
                    background: rgba(108, 92, 231, 0.05);
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .favorite-chip.leaf {
                    background: var(--color-primary);
                    color: white;
                    border: none;
                    justify-content: center;
                    text-align: center;
                }
                .favorite-chip.leaf:hover {
                    background: #5b4bc4;
                }
                .btn-back {
                    background: #f0f0f0;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 0.75rem;
                    cursor: pointer;
                }
                .btn-back:hover {
                    background: #e0e0e0;
                }
            `}</style>
        </div>
    );
}
