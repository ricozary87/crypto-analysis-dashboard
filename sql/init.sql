-- Database initialization script for PostgreSQL
-- This script sets up the initial database structure

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for performance (will be created by SQLAlchemy migrations)
-- This file can be used for additional database setup if needed