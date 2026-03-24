BEGIN;

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    source_goal_id INTEGER,
    current_stage_key TEXT NOT NULL DEFAULT 'requirement',
    status TEXT NOT NULL DEFAULT 'active',
    risk_level TEXT DEFAULT 'medium',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_stage_states (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stage_key TEXT NOT NULL,
    stage_status TEXT NOT NULL DEFAULT 'pending',
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    waiting_for_human BOOLEAN NOT NULL DEFAULT FALSE,
    entered_at TIMESTAMPTZ,
    exited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (project_id, stage_key)
);

CREATE TABLE IF NOT EXISTS requirement_cards (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_no INTEGER NOT NULL DEFAULT 1,
    title TEXT,
    summary TEXT,
    target_users TEXT,
    problem_statement TEXT,
    scope_in JSONB NOT NULL DEFAULT '[]'::jsonb,
    scope_out JSONB NOT NULL DEFAULT '[]'::jsonb,
    success_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
    risks JSONB NOT NULL DEFAULT '[]'::jsonb,
    dependencies JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'draft',
    confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clarification_rounds (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    requirement_card_id INTEGER REFERENCES requirement_cards(id) ON DELETE SET NULL,
    round_no INTEGER NOT NULL DEFAULT 1,
    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    answers_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    resolved_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prototype_specs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    requirement_card_id INTEGER REFERENCES requirement_cards(id) ON DELETE SET NULL,
    version_no INTEGER NOT NULL DEFAULT 1,
    ia_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    page_flow_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    module_map_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    api_draft_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    figma_url TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orchestration_plans (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    prototype_spec_id INTEGER REFERENCES prototype_specs(id) ON DELETE SET NULL,
    version_no INTEGER NOT NULL DEFAULT 1,
    epic_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    feature_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    tasks_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    agent_jobs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    acceptance_criteria_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    dependency_graph_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS delivery_packages (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    summary_md TEXT,
    prototype_refs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    engineering_refs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    testing_refs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    process_refs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    next_step_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    published_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_transitions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    from_stage_key TEXT,
    to_stage_key TEXT NOT NULL,
    transition_reason TEXT,
    triggered_by TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS human_approvals (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    approval_type TEXT NOT NULL,
    target_ref_type TEXT NOT NULL,
    target_ref_id INTEGER,
    decision TEXT NOT NULL DEFAULT 'pending',
    note TEXT,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_jobs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    orchestration_plan_id INTEGER REFERENCES orchestration_plans(id) ON DELETE SET NULL,
    job_type TEXT NOT NULL,
    title TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending',
    executor_key TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
