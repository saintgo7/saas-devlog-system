-- Migration: Add Development Activity Tracking Tables
-- Version: 001
-- Date: 2024-12-25
-- Description: Git 커밋 이력, 일일 개발 통계, 작업 로그, 프로젝트 연결 테이블 추가

-- ============================================
-- Enums
-- ============================================

-- 작업 로그 카테고리
DO $$ BEGIN
    CREATE TYPE worklog_category AS ENUM (
        'feature', 'bugfix', 'refactor', 'docs',
        'meeting', 'research', 'review', 'deploy', 'test', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 작업 로그 소스
DO $$ BEGIN
    CREATE TYPE worklog_source AS ENUM ('manual', 'auto_git', 'auto_session');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- Tables
-- ============================================

-- 1. Git 커밋 이력
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

    -- 유니크 제약조건 (프로젝트 내 커밋 해시 중복 방지)
    UNIQUE(project_id, commit_hash)
);

-- 2. 일일 개발 통계
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

    -- 유니크 제약조건 (워크스테이션별 일일 통계)
    UNIQUE(workstation_id, date)
);

-- 3. 작업 로그
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

-- 4. 프로젝트 연결 (동일 프로젝트 매핑)
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

-- Git 커밋 인덱스
CREATE INDEX IF NOT EXISTS idx_git_commits_workstation ON git_commits(workstation_id);
CREATE INDEX IF NOT EXISTS idx_git_commits_project ON git_commits(project_id);
CREATE INDEX IF NOT EXISTS idx_git_commits_date ON git_commits(committed_at);
CREATE INDEX IF NOT EXISTS idx_git_commits_author ON git_commits(author_email);

-- 일일 통계 인덱스
CREATE INDEX IF NOT EXISTS idx_daily_dev_stats_workstation ON daily_dev_stats(workstation_id);
CREATE INDEX IF NOT EXISTS idx_daily_dev_stats_date ON daily_dev_stats(date);

-- 작업 로그 인덱스
CREATE INDEX IF NOT EXISTS idx_work_logs_workstation ON work_logs(workstation_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_user ON work_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_project ON work_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_date ON work_logs(started_at);
CREATE INDEX IF NOT EXISTS idx_work_logs_category ON work_logs(category);

-- 프로젝트 연결 인덱스
CREATE INDEX IF NOT EXISTS idx_project_links_name ON project_links(name);
CREATE INDEX IF NOT EXISTS idx_project_links_remote_url ON project_links(remote_url);

-- ============================================
-- Comments
-- ============================================

COMMENT ON TABLE git_commits IS 'Git 커밋 이력 - 모든 워크스테이션의 커밋 기록';
COMMENT ON TABLE daily_dev_stats IS '일일 개발 통계 - 워크스테이션별 일일 개발 활동 요약';
COMMENT ON TABLE work_logs IS '작업 로그 - 수동/자동 작업 내역 기록';
COMMENT ON TABLE project_links IS '프로젝트 연결 - 여러 워크스테이션의 동일 프로젝트 매핑';

COMMENT ON COLUMN git_commits.additions IS '추가된 라인 수';
COMMENT ON COLUMN git_commits.deletions IS '삭제된 라인 수';
COMMENT ON COLUMN daily_dev_stats.dev_time_minutes IS '추정 개발 시간 (분)';
COMMENT ON COLUMN work_logs.source IS '로그 생성 방식: manual(수동), auto_git(Git 기반), auto_session(세션 기반)';

-- ============================================
-- Migration Complete
-- ============================================
