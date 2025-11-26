[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE debtors (
    national_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    financial_data_source TEXT,
    user_username TEXT REFERENCES users(username)
);
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username),

    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,

    timestamp TIMESTAMP DEFAULT NOW(),
    details TEXT
);

CREATE TABLE financial_data (
    id BIGSERIAL PRIMARY KEY,
    debtor_id BIGINT REFERENCES debtors(national_id),
    year INT NOT NULL,

    assets NUMERIC,
    liabilities NUMERIC,
    solvability_score DOUBLE PRECISION,

    created_at TIMESTAMPTZ DEFAULT NOW()
);
