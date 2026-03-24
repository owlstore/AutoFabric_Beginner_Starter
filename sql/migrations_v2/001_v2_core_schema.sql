BEGIN;

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_key VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    current_stage VARCHAR(64) NOT NULL DEFAULT 'requirement',
    status VARCHAR(64) NOT NULL DEFAULT 'draft',
    priority VARCHAR(32) NOT NULL DEFAULT 'normal',
    source_goal_id INTEGER,
    owner VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_stage_states (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stage_name VARCHAR(64) NOT NULL,
    stage_status VARCHAR(64) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_actor VARCHAR(255),
    last_note TEXT,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(project_id, stage_name)
);

CREATE TABLE IF NOT EXISTS requirement_cards (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    raw_input TEXT,
    normalized_goal TEXT,
    acceptance_criteria_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    constraints_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    priority VARCHAR(32) NOT NULL DEFAULT 'normal',
    status VARCHAR(64) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clarification_rounds (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    round_no INTEGER NOT NULL DEFAULT 1,
    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    answers_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    decision_summary TEXT,
    status VARCHAR(64) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prototype_specs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_no INTEGER NOT NULL DEFAULT 1,
    spec_summary TEXT,
    information_architecture_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    ui_notes_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    figma_ref TEXT,
    status VARCHAR(64) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orchestration_plans (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_no INTEGER NOT NULL DEFAULT 1,
    task_graph_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    agent_plan_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_strategy_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    risk_notes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(64) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS testing_runs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_no INTEGER NOT NULL DEFAULT 1,
    test_summary TEXT,
    test_report_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    pass_count INTEGER NOT NULL DEFAULT 0,
    fail_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(64) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS delivery_packages (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_no INTEGER NOT NULL DEFAULT 1,
    delivery_summary TEXT,
    artifacts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    release_notes TEXT,
    handoff_notes TEXT,
    status VARCHAR(64) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_transitions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    from_stage VARCHAR(64),
    to_stage VARCHAR(64) NOT NULL,
    transition_status VARCHAR(64) NOT NULL DEFAULT 'requested',
    triggered_by VARCHAR(255),
    reason TEXT,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS human_approvals (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stage_name VARCHAR(64) NOT NULL,
    approval_type VARCHAR(64) NOT NULL,
    decision VARCHAR(64) NOT NULL DEFAULT 'pending',
    decided_by VARCHAR(255),
    decision_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_jobs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stage_name VARCHAR(64) NOT NULL,
    executor_type VARCHAR(64) NOT NULL,
    job_key VARCHAR(128),
    input_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(64) NOT NULL DEFAULT 'queued',
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_artifact_links (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    artifact_id INTEGER NOT NULL,
    artifact_type VARCHAR(64),
    stage_name VARCHAR(64),
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_current_stage ON projects(current_stage);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_project_stage_states_project_id ON project_stage_states(project_id);
CREATE INDEX IF NOT EXISTS idx_requirement_cards_project_id ON requirement_cards(project_id);
CREATE INDEX IF NOT EXISTS idx_clarification_rounds_project_id ON clarification_rounds(project_id);
CREATE INDEX IF NOT EXISTS idx_prototype_specs_project_id ON prototype_specs(project_id);
CREATE INDEX IF NOT EXISTS idx_orchestration_plans_project_id ON orchestration_plans(project_id);
CREATE INDEX IF NOT EXISTS idx_testing_runs_project_id ON testing_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_delivery_packages_project_id ON delivery_packages(project_id);
CREATE INDEX IF NOT EXISTS idx_stage_transitions_project_id ON stage_transitions(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_project_id ON agent_jobs(project_id);

COMMIT;
