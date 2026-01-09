-- Database Initialization Script for Evolution of Todo - Phase II
-- This script creates the database schema from scratch
--
-- Usage:
--   psql -U postgres -d todo_db -f init.sql
--
-- Note: In production, SQLModel will create tables automatically.
--       This script is provided for manual setup or testing.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- Index for email lookups (login)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

COMMENT ON TABLE users IS 'User accounts for authentication and task ownership';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID)';
COMMENT ON COLUMN users.email IS 'User email address (unique, used for login)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password (never plain text)';
COMMENT ON COLUMN users.created_at IS 'Account creation timestamp (UTC)';

-- ============================================================================
-- TASKS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    updated_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON tasks(user_id, created_at DESC);

COMMENT ON TABLE tasks IS 'Todo tasks with multi-user support (Phase II evolution of TodoItem)';
COMMENT ON COLUMN tasks.id IS 'Unique task identifier (UUID)';
COMMENT ON COLUMN tasks.user_id IS 'Owner of the task (foreign key to users)';
COMMENT ON COLUMN tasks.title IS 'Task description (required, non-empty)';
COMMENT ON COLUMN tasks.description IS 'Optional detailed description';
COMMENT ON COLUMN tasks.status IS 'Task status: pending or completed';
COMMENT ON COLUMN tasks.created_at IS 'Task creation timestamp (UTC)';
COMMENT ON COLUMN tasks.updated_at IS 'Last modification timestamp (UTC)';

-- ============================================================================
-- TRIGGER: Auto-update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA (Development Only)
-- ============================================================================

-- Insert test user (password: "password123" hashed with bcrypt)
-- NOTE: Remove this in production!
INSERT INTO users (id, email, password_hash)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYvFz0Ow5Wi'
) ON CONFLICT (email) DO NOTHING;

-- Insert test tasks
INSERT INTO tasks (user_id, title, description, status)
VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Milk, eggs, bread', 'pending'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Write documentation', 'Complete Phase II docs', 'completed'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Review pull requests', NULL, 'pending')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables were created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('users', 'tasks');

-- Verify indexes were created
SELECT indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('users', 'tasks');

-- Count test data
SELECT
    (SELECT COUNT(*) FROM users) as user_count,
    (SELECT COUNT(*) FROM tasks) as task_count;

-- Show sample data
SELECT
    t.id,
    t.title,
    t.status,
    u.email as owner_email
FROM tasks t
JOIN users u ON t.user_id = u.id
LIMIT 5;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Tables: users, tasks';
    RAISE NOTICE 'Extensions: uuid-ossp';
    RAISE NOTICE 'Test user: test@example.com (password: password123)';
END $$;
