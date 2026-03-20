CREATE TABLE IF NOT EXISTS goals (
  id SERIAL PRIMARY KEY,
  raw_input TEXT NOT NULL,
  goal_type VARCHAR(50) NOT NULL DEFAULT 'environment_build',
  parsed_goal JSONB NOT NULL DEFAULT '{}'::jsonb,
  risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outcomes (
  id SERIAL PRIMARY KEY,
  goal_id INTEGER NOT NULL REFERENCES goals(id),
  title VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  current_result JSONB NOT NULL DEFAULT '{}'::jsonb,
  next_action TEXT,
  risk_boundary TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS executions (
  id SERIAL PRIMARY KEY,
  outcome_id INTEGER NOT NULL REFERENCES outcomes(id),
  executor_type VARCHAR(50) NOT NULL,
  input_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  output_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  status VARCHAR(50) NOT NULL DEFAULT 'queued',
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS verifications (
  id SERIAL PRIMARY KEY,
  outcome_id INTEGER NOT NULL REFERENCES outcomes(id),
  check_name VARCHAR(100) NOT NULL,
  result VARCHAR(20) NOT NULL,
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS artifacts (
  id SERIAL PRIMARY KEY,
  outcome_id INTEGER NOT NULL REFERENCES outcomes(id),
  artifact_type VARCHAR(50) NOT NULL,
  file_path TEXT NOT NULL,
  checksum TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flow_events (
  id SERIAL PRIMARY KEY,
  outcome_id INTEGER NOT NULL REFERENCES outcomes(id),
  from_status VARCHAR(50),
  to_status VARCHAR(50) NOT NULL,
  trigger_type VARCHAR(50) NOT NULL,
  note TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
