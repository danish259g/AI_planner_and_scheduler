import React from 'react';

export default function Favorites({ onQuickAdd }) {
    const favorites = [
        "Go for a run (30 mins)",
        "Buy groceries (60 mins)",
        "Team Sync (45 mins)",
        "Study Session (120 mins)",
        "Call Mom (20 mins)"
    ];

    return (
        <div className="favorites-container">
            <h3>Quick Add / Favorites</h3>
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
        </div>
    );
}
