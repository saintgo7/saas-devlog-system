-- Workstation Manager - Database Initialization Script
-- PostgreSQL 15+

-- ============================================
-- Extensions
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================
-- Enums
-- ============================================

-- 워크스테이션 OS 타입
DO $$ BEGIN
    CREATE TYPE os_type AS ENUM ('windows', 'linux', 'macos');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 워크스테이션 상태
DO $$ BEGIN
    CREATE TYPE workstation_status AS ENUM ('online', 'offline', 'unknown', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 알림 심각도
DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('info', 'warning', 'error', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 사용자 역할
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'operator', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 알림 상태
DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 프로젝트 타입
DO $$ BEGIN
    CREATE TYPE project_type AS ENUM ('nodejs', 'python', 'rust', 'go', 'java', 'php', 'ruby', 'cpp', 'c', 'docker', 'unknown');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 개발 상태
DO $$ BEGIN
    CREATE TYPE dev_status AS ENUM ('clean', 'in_progress', 'unpushed', 'behind');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 작업 로그 카테고리
DO $$ BEGIN
    CREATE TYPE worklog_category AS ENUM ('feature', 'bugfix', 'refactor', 'docs', 'meeting', 'research', 'review', 'deploy', 'test', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 작업 로그 소스
DO $$ BEGIN
    CREATE TYPE worklog_source AS ENUM ('manual', 'auto', 'import');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- Tables
-- ============================================

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role user_role NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    profile_image_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT false,
    notification_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 워크스테이션 테이블
CREATE TABLE IF NOT EXISTS workstations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hostname VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    os_type os_type NOT NULL,
    os_version VARCHAR(100),
    status workstation_status DEFAULT 'offline',
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    location VARCHAR(255),
    description TEXT,
    tags TEXT[],

    -- SSH/RDP 연결 정보
    ssh_enabled BOOLEAN DEFAULT false,
    ssh_port INTEGER DEFAULT 22,
    ssh_username VARCHAR(100),
    ssh_password_encrypted TEXT,
    rdp_enabled BOOLEAN DEFAULT false,
    rdp_port INTEGER DEFAULT 3389,
    rdp_username VARCHAR(100),
    rdp_password_encrypted TEXT,

    -- 에이전트 정보
    agent_version VARCHAR(50),
    agent_last_seen TIMESTAMP WITH TIME ZONE,

    -- 실시간 메트릭 (캐시용)
    cpu_percent DECIMAL(5, 2) DEFAULT 0,
    memory_percent DECIMAL(5, 2) DEFAULT 0,
    disk_percent DECIMAL(5, 2) DEFAULT 0,

    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_ssh_port CHECK (ssh_port BETWEEN 1 AND 65535),
    CONSTRAINT valid_rdp_port CHECK (rdp_port BETWEEN 1 AND 65535)
);

-- 시스템 사양 테이블
CREATE TABLE IF NOT EXISTS system_specs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,

    -- CPU 정보
    cpu_model VARCHAR(255),
    cpu_cores INTEGER,
    cpu_threads INTEGER,
    cpu_frequency_mhz DECIMAL(10, 2),
    cpu_vendor VARCHAR(100),
    cpu_architecture VARCHAR(20),

    -- 메모리 정보
    total_memory_gb DECIMAL(10, 2),
    ram_total_bytes BIGINT,
    ram_type VARCHAR(20),
    ram_speed_mhz INTEGER,
    ram_slots_used INTEGER,
    ram_slots_total INTEGER,

    -- GPU 정보
    gpu_info JSONB,
    gpu_model VARCHAR(255),
    gpu_memory_gb DECIMAL(10, 2),
    gpu_driver_version VARCHAR(50),

    -- 스토리지 정보
    storage_info JSONB,
    storage_total_bytes BIGINT,
    storage_type VARCHAR(20),

    -- 네트워크 정보
    network_info JSONB,
    primary_mac VARCHAR(17),
    primary_ip VARCHAR(45),

    -- 기타 하드웨어 정보
    motherboard VARCHAR(255),
    motherboard_manufacturer VARCHAR(100),
    bios_version VARCHAR(100),
    bios_vendor VARCHAR(100),
    serial_number VARCHAR(100),
    system_manufacturer VARCHAR(100),
    system_model VARCHAR(100),

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_workstation_spec UNIQUE (workstation_id)
);

-- 시스템 메트릭 테이블 (시계열 데이터)
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,

    -- CPU 메트릭
    cpu_percent DECIMAL(5, 2),
    cpu_user_percent DECIMAL(5, 2),
    cpu_system_percent DECIMAL(5, 2),
    cpu_iowait_percent DECIMAL(5, 2),
    load_avg_1min DECIMAL(6, 2),
    load_avg_5min DECIMAL(6, 2),
    load_avg_15min DECIMAL(6, 2),

    -- 메모리 메트릭
    memory_percent DECIMAL(5, 2),
    memory_used_bytes BIGINT,
    memory_available_bytes BIGINT,
    swap_percent DECIMAL(5, 2),
    swap_used_bytes BIGINT,

    -- 디스크 메트릭
    disk_percent DECIMAL(5, 2),
    disk_read_bytes BIGINT,
    disk_write_bytes BIGINT,
    disk_iops_read INTEGER,
    disk_iops_write INTEGER,
    disk_usage JSONB,

    -- 네트워크 메트릭
    network_in_bytes BIGINT,
    network_out_bytes BIGINT,
    network_packets_in BIGINT,
    network_packets_out BIGINT,

    -- 프로세스 정보
    process_count INTEGER,
    thread_count INTEGER,
    handle_count INTEGER,
    active_users INTEGER,

    -- 온도
    cpu_temp_celsius DECIMAL(5, 2),
    gpu_temp_celsius DECIMAL(5, 2),

    -- Legacy columns (for backward compatibility)
    cpu_usage_percent DECIMAL(5, 2),
    cpu_frequency_current_mhz DECIMAL(10, 2),
    cpu_temperature_celsius DECIMAL(5, 2),
    memory_used_gb DECIMAL(10, 2),
    swap_used_gb DECIMAL(10, 2),
    disk_io_read_mbps DECIMAL(10, 2),
    disk_io_write_mbps DECIMAL(10, 2),
    network_sent_mbps DECIMAL(10, 2),
    network_recv_mbps DECIMAL(10, 2),
    gpu_usage_percent DECIMAL(5, 2),
    gpu_memory_used_gb DECIMAL(10, 2),
    gpu_temperature_celsius DECIMAL(5, 2),

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 설치된 프로그램 테이블
CREATE TABLE IF NOT EXISTS installed_apps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    version VARCHAR(100),
    publisher VARCHAR(200),
    install_date DATE,
    install_location VARCHAR(1000),
    size_bytes BIGINT,
    size_mb DECIMAL(10, 2),

    category VARCHAR(50),
    is_system_app BOOLEAN DEFAULT false,

    -- Windows specific
    uninstall_string VARCHAR(2000),
    registry_key VARCHAR(500),

    -- Linux specific
    package_manager VARCHAR(20),
    package_name VARCHAR(200),

    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_verified TIMESTAMP WITH TIME ZONE,
    last_scanned TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,

    CONSTRAINT unique_app_per_workstation UNIQUE (workstation_id, name, version)
);

-- 사용 세션 테이블
CREATE TABLE IF NOT EXISTS usage_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    session_type VARCHAR(20),
    login_time TIMESTAMP WITH TIME ZONE NOT NULL,
    logout_time TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    active_minutes INTEGER,
    idle_minutes INTEGER,
    client_ip INET,
    client_hostname VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    termination_reason VARCHAR(100),
    session_duration_minutes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 프로그램 실행 기록 테이블
CREATE TABLE IF NOT EXISTS app_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,
    session_id UUID REFERENCES usage_sessions(id) ON DELETE SET NULL,
    process_name VARCHAR(200),
    app_name VARCHAR(255),
    executable_path VARCHAR(1000),
    window_title VARCHAR(500),
    username VARCHAR(100),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    duration_minutes INTEGER,
    cpu_usage_percent DECIMAL(5, 2),
    cpu_usage_avg DECIMAL(5, 2),
    memory_usage_bytes BIGINT,
    memory_usage_avg_mb DECIMAL(10, 2),
    pid INTEGER,
    parent_pid INTEGER,
    command_line TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 알림 테이블
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID REFERENCES workstations(id) ON DELETE CASCADE,
    alert_type VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    severity severity_level NOT NULL,
    status alert_status DEFAULT 'active',

    -- 메트릭 관련
    metric_name VARCHAR(100),
    threshold_value DECIMAL(10, 2),
    actual_value DECIMAL(10, 2),

    -- 알림 소스
    source VARCHAR(100),
    category VARCHAR(100),

    -- 메타데이터
    metadata JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id)
);

-- API 키 테이블 (에이전트 인증)
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    workstation_id UUID REFERENCES workstations(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- ============================================
-- 개발 활동 추적 시스템 테이블
-- ============================================

-- 개발 프로젝트 테이블
CREATE TABLE IF NOT EXISTS dev_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    path VARCHAR(1000) NOT NULL,
    project_type project_type DEFAULT 'unknown',
    size_bytes BIGINT,

    -- Git 정보
    git_branch VARCHAR(255),
    git_remote_url VARCHAR(500),
    git_status dev_status DEFAULT 'clean',
    git_modified INTEGER DEFAULT 0,
    git_staged INTEGER DEFAULT 0,
    git_untracked INTEGER DEFAULT 0,
    git_ahead INTEGER DEFAULT 0,
    git_behind INTEGER DEFAULT 0,

    -- 마지막 커밋 정보
    last_commit_hash VARCHAR(40),
    last_commit_message VARCHAR(500),
    last_commit_date TIMESTAMP WITH TIME ZONE,
    last_commit_author VARCHAR(255),

    -- 메타 정보
    last_modified TIMESTAMP WITH TIME ZONE,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_scanned TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,

    CONSTRAINT unique_project_per_workstation UNIQUE (workstation_id, path)
);

-- Git 커밋 이력 테이블
CREATE TABLE IF NOT EXISTS git_commits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES dev_projects(id) ON DELETE CASCADE,

    -- 커밋 정보
    commit_hash VARCHAR(40) NOT NULL,
    message TEXT,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    committed_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- 변경 통계
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_commit_per_project UNIQUE (project_id, commit_hash)
);

-- 일일 개발 통계 테이블
CREATE TABLE IF NOT EXISTS daily_dev_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID NOT NULL REFERENCES workstations(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- 커밋 통계
    total_commits INTEGER DEFAULT 0,
    total_additions INTEGER DEFAULT 0,
    total_deletions INTEGER DEFAULT 0,

    -- 프로젝트 통계
    active_projects INTEGER DEFAULT 0,
    top_project_id UUID REFERENCES dev_projects(id) ON DELETE SET NULL,

    -- 개발 시간 (분)
    dev_time_minutes INTEGER DEFAULT 0,

    -- 작성자별 커밋 수 (JSON)
    commits_by_author JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_daily_stats UNIQUE (workstation_id, date)
);

-- 작업 로그 테이블
CREATE TABLE IF NOT EXISTS work_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workstation_id UUID REFERENCES workstations(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    project_id UUID REFERENCES dev_projects(id) ON DELETE SET NULL,

    -- 작업 정보
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category worklog_category DEFAULT 'other',

    -- 시간 정보
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,

    -- 메타데이터
    tags JSONB DEFAULT '[]',
    related_commits JSONB DEFAULT '[]',
    source worklog_source DEFAULT 'manual',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 프로젝트 연결 테이블 (동일 프로젝트 매핑)
CREATE TABLE IF NOT EXISTS project_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- 통합 프로젝트 정보
    name VARCHAR(255) NOT NULL,
    description TEXT,
    remote_url VARCHAR(500),

    -- 연결된 DevProject ID 목록
    linked_project_ids JSONB DEFAULT '[]',

    -- 통계 캐시
    total_commits INTEGER DEFAULT 0,
    total_additions INTEGER DEFAULT 0,
    total_deletions INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indexes
-- ============================================

-- Workstations
CREATE INDEX IF NOT EXISTS idx_workstations_status ON workstations(status);
CREATE INDEX IF NOT EXISTS idx_workstations_os_type ON workstations(os_type);
CREATE INDEX IF NOT EXISTS idx_workstations_hostname ON workstations(hostname);
CREATE INDEX IF NOT EXISTS idx_workstations_agent_last_seen ON workstations(agent_last_seen);

-- System Metrics (시계열 쿼리 최적화)
CREATE INDEX IF NOT EXISTS idx_metrics_workstation_timestamp ON system_metrics(workstation_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp DESC);

-- Installed Apps
CREATE INDEX IF NOT EXISTS idx_installed_apps_workstation ON installed_apps(workstation_id);
CREATE INDEX IF NOT EXISTS idx_installed_apps_name ON installed_apps(name);

-- Usage Sessions
CREATE INDEX IF NOT EXISTS idx_usage_sessions_workstation ON usage_sessions(workstation_id);
CREATE INDEX IF NOT EXISTS idx_usage_sessions_active ON usage_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_usage_sessions_login_time ON usage_sessions(login_time DESC);

-- App History
CREATE INDEX IF NOT EXISTS idx_app_history_workstation ON app_history(workstation_id);
CREATE INDEX IF NOT EXISTS idx_app_history_start_time ON app_history(start_time DESC);

-- Alerts
CREATE INDEX IF NOT EXISTS idx_alerts_workstation ON alerts(workstation_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- Users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Dev Projects
CREATE INDEX IF NOT EXISTS idx_dev_projects_workstation ON dev_projects(workstation_id);
CREATE INDEX IF NOT EXISTS idx_dev_projects_name ON dev_projects(name);
CREATE INDEX IF NOT EXISTS idx_dev_projects_remote_url ON dev_projects(git_remote_url);

-- Git Commits
CREATE INDEX IF NOT EXISTS idx_git_commits_workstation ON git_commits(workstation_id);
CREATE INDEX IF NOT EXISTS idx_git_commits_project ON git_commits(project_id);
CREATE INDEX IF NOT EXISTS idx_git_commits_date ON git_commits(committed_at DESC);
CREATE INDEX IF NOT EXISTS idx_git_commits_author ON git_commits(author_email);

-- Daily Dev Stats
CREATE INDEX IF NOT EXISTS idx_daily_dev_stats_workstation ON daily_dev_stats(workstation_id);
CREATE INDEX IF NOT EXISTS idx_daily_dev_stats_date ON daily_dev_stats(date DESC);

-- Work Logs
CREATE INDEX IF NOT EXISTS idx_work_logs_workstation ON work_logs(workstation_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_user ON work_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_project ON work_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_date ON work_logs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_work_logs_category ON work_logs(category);

-- Project Links
CREATE INDEX IF NOT EXISTS idx_project_links_name ON project_links(name);
CREATE INDEX IF NOT EXISTS idx_project_links_remote_url ON project_links(remote_url);

-- ============================================
-- Triggers for updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_workstations_updated_at ON workstations;
CREATE TRIGGER update_workstations_updated_at BEFORE UPDATE ON workstations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_system_specs_updated_at ON system_specs;
CREATE TRIGGER update_system_specs_updated_at BEFORE UPDATE ON system_specs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Initial Data (admin user)
-- ============================================

-- Default admin user (password: admin1234)
-- IMPORTANT: Change this password immediately after first login!
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES (
    'admin',
    'admin@workstation.local',
    '$2b$12$tGz28dQjBmlpTF/lmuOyk.qhwG61yspYL22wXwKd1qiTRnTNB3p66',
    'System Administrator',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- ============================================
-- Permissions
-- ============================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
