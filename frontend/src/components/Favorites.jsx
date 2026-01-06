import React from 'react';

export default function Favorites({ onQuickAdd }) {
    const favorites = [
        { title: "Geometry", duration_mins: 60, tag: "Quantitative" },
        { title: "Analogies", duration_mins: 45, tag: "Verbal" },
        { title: "ENG Vocabulary", duration_mins: 30, tag: "English" },
        { title: "Essay Writing", duration_mins: 35, tag: "Essay" },
        { title: "Full Simulation", duration_mins: 200, tag: "Simulation" },
        { title: "Section Simulation", duration_mins: 25, tag: "Simulation" },
        { title: "Course Lesson", duration_mins: 180, tag: "Class", is_locked: true },
        { title: "Critical Reasoning", duration_mins: 60, tag: "Verbal" },
        { title: "Algebra", duration_mins: 60, tag: "Quantitative" },
        { title: "ENG Reading Comp", duration_mins: 60, tag: "English" }
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
