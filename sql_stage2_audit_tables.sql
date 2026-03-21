CREATE TABLE IF NOT EXISTS executions (
    id SERIAL PRIMARY KEY,
    outcome_id INTEGER NOT NULL,
    executor_name VARCHAR(100) NOT NULL,
    task_name VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    input_payload JSONB,
    output_payload JSONB,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS artifacts (
    id SERIAL PRIMARY KEY,
    outcome_id INTEGER NOT NULL,
    artifact_type VARCHAR(100) NOT NULL,
    file_path TEXT,
    artifact_ref TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS verifications (
    id SERIAL PRIMARY KEY,
    outcome_id INTEGER NOT NULL,
    verifier_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    checks JSONB,
    summary JSONB,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_executions_outcome_id ON executions(outcome_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_outcome_id ON artifacts(outcome_id);
CREATE INDEX IF NOT EXISTS idx_verifications_outcome_id ON verifications(outcome_id);
