-- SuperDev Suite Database Initialization
-- This script runs on PostgreSQL container startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create main application schema
CREATE SCHEMA IF NOT EXISTS superdev;

-- Create users table
CREATE TABLE IF NOT EXISTS superdev.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create projects table
CREATE TABLE IF NOT EXISTS superdev.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    slug VARCHAR(100),
    owner_id UUID REFERENCES superdev.users(id) ON DELETE CASCADE,
    visibility VARCHAR(50) DEFAULT 'private',
    settings JSONB DEFAULT '{}',
    repository_url VARCHAR(500),
    repository_branch VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create project members table
CREATE TABLE IF NOT EXISTS superdev.project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES superdev.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES superdev.users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

-- Create API keys table
CREATE TABLE IF NOT EXISTS superdev.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    user_id UUID REFERENCES superdev.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES superdev.projects(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON superdev.users(email);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON superdev.projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_project_members_user ON superdev.project_members(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON superdev.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_project ON superdev.api_keys(project_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON superdev.api_keys(key_hash);

-- Insert default admin user (password: SuperDev@2025)
INSERT INTO superdev.users (email, username, hashed_password, full_name, is_superuser, is_verified)
VALUES (
    'admin@superdev.com',
    'admin',
    '\$2b\$12\$QlZX4Sce2/JWDwn92PNOAuzvMbHBem7O5cLjNFZ46VvOvK7Fgiedu',
    'SuperDev Admin',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT USAGE ON SCHEMA superdev TO superdev;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA superdev TO superdev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA superdev TO superdev;