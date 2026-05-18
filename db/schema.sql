-- ==========================================
-- Repo Autopilot Enterprise Database Schema
-- Target: PostgreSQL
-- ==========================================

-- Enable UUID extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    url VARCHAR(512) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    default_branch VARCHAR(100) DEFAULT 'main',
    health_score DECIMAL(5, 2) DEFAULT 100.00,
    is_active BOOLEAN DEFAULT TRUE,
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Health Scores history table
CREATE TABLE IF NOT EXISTS health_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    coverage DECIMAL(5, 2) DEFAULT 0.00,
    security_vulns INT DEFAULT 0,
    code_complexity INT DEFAULT 0, -- e.g., Cognitive/Cyclomatic complexity
    linter_errors INT DEFAULT 0,
    health_score DECIMAL(5, 2) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Job queue and history table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'repo-analyzer', 'pr-generator', 'ci-fixer', 'git-executor'
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    payload JSONB, -- Job specific arguments (branch, PR#, etc.)
    result JSONB, -- Job execution results, logs, errors
    worker_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Risk and Vulnerability assessments table
CREATE TABLE IF NOT EXISTS risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    risk_level VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    dependency_graph_risk JSONB, -- Checked and parsed dependency issues
    architectural_risks JSONB, -- List of modularity/coupling flags
    raw_analysis TEXT,
    last_checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI Decision & Audit Logging table (governance & safety compliance)
CREATE TABLE IF NOT EXISTS ai_decision_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    decision_type VARCHAR(100) NOT NULL, -- e.g., 'code-fix', 'pr-review', 'dependency-update'
    input_prompt TEXT NOT NULL,
    ai_reasoning TEXT NOT NULL,
    proposed_diff TEXT,
    governance_passed BOOLEAN DEFAULT TRUE,
    governance_message TEXT,
    user_approved BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(255),
    action_taken VARCHAR(255), -- 'pr_opened', 'job_blocked', 'override_executed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index creation for search optimizations
CREATE INDEX IF NOT EXISTS idx_repositories_health_score ON repositories(health_score);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_repository_id ON jobs(repository_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_repo_id ON ai_decision_audit_logs(repository_id);
CREATE INDEX IF NOT EXISTS idx_health_scores_repo_id ON health_scores(repository_id);
