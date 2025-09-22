-- db/schema.sql
-- PostgreSQL DDL for Employee Performance Management System

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    department VARCHAR(100),
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    hire_date DATE,
    role VARCHAR(50),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_manager ON employees(manager_id);

CREATE TABLE review_cycles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('active','closed')),
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_cycles_end_date ON review_cycles(end_date);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    reviewer_id INTEGER NOT NULL REFERENCES employees(id),
    cycle_id INTEGER NOT NULL REFERENCES review_cycles(id),
    review_type VARCHAR(10) NOT NULL CHECK (review_type IN ('self','manager','peer')),
    status VARCHAR(10) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','submitted')),
    submitted_date TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    -- Prevent exact duplicate same reviewer creating same review type for same employee & cycle
    UNIQUE (employee_id, cycle_id, reviewer_id, review_type)
);

CREATE INDEX idx_reviews_employee ON reviews(employee_id);
CREATE INDEX idx_reviews_reviewer ON reviews(reviewer_id);
CREATE INDEX idx_reviews_cycle ON reviews(cycle_id);
CREATE INDEX idx_reviews_type_status ON reviews(review_type, status);

CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    criteria VARCHAR(20) NOT NULL CHECK (criteria IN ('technical','communication','leadership','goals')),
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 10),
    comments TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_scores_review ON scores(review_id);

CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    cycle_id INTEGER NOT NULL REFERENCES review_cycles(id),
    description TEXT,
    target_date DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('not_started','in_progress','completed')),
    progress INTEGER NOT NULL CHECK (progress >= 0 AND progress <= 100),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_goals_employee ON goals(employee_id);
CREATE INDEX idx_goals_cycle ON goals(cycle_id);

-- 'users' in spec; in Django we use auth_user; but we also create a mapping table for role if you want to keep a separate 'users' table:
CREATE TABLE app_users (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(512) NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('employee','manager','hr')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_appusers_employee ON app_users(employee_id);

-- Audit log table for score changes
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50), -- 'score', 'review', 'goal'
    entity_id INTEGER,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by INTEGER, -- app_users.id or auth_user.id
    changed_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
