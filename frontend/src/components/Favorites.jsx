import React from 'react';

export default function Favorites({ onQuickAdd }) {
    const favorites = [
        { title: "Go for a run", duration_mins: 45, tag: "Health" },
        { title: "Buy groceries", duration_mins: 60, tag: "Errand" },
        { title: "Team Sync", duration_mins: 30, tag: "Work" },
        { title: "Deep Work", duration_mins: 120, tag: "Work" },
        { title: "Call Mom", duration_mins: 15, tag: "Personal" }
    ];

    return (
        <div className="favorites-grid">
            {favorites.map((fav, idx) => (
                <button
                    key={idx}
                    className="favorite-chip"
                    onClick={() => onQuickAdd(fav)}
                >
                    + {fav.title}
                </button>
            ))}
        </div>
    );
}
