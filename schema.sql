CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    requester_name TEXT NOT NULL,
    email TEXT NOT NULL,

    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,

    priority TEXT NOT NULL
        CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),

    status TEXT NOT NULL DEFAULT 'Open'
        CHECK (status IN (
            'Open',
            'In Progress',
            'Pending User',
            'Escalated',
            'Resolved',
            'Closed'
        )),

    assigned_analyst TEXT,

    investigation_notes TEXT,

    root_cause TEXT,

    resolution TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP
);