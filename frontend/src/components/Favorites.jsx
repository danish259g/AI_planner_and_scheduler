import React from 'react';

export default function Favorites({ onQuickAdd }) {
    const favorites = [
        "Go for a run",
        "Buy groceries",
        "Team Sync",
        "Deep Work",
        "Call Mom"
    ];

    return (
        <div className="favorites-grid">
            {favorites.map((fav, idx) => (
                <button
                    key={idx}
                    className="favorite-chip"
                    onClick={() => onQuickAdd(fav)}
                >
                    + {fav}
                </button>
            ))}
        </div>
    );
}
