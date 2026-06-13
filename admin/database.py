#!/usr/bin/env python3
"""
SQLite Database Schema for Dev Log Admin
"""
import sqlite3

DB_PATH = "devlog.db"

def init_db():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            repository_url TEXT,
            tech_stack TEXT,  -- JSON string
            html_url TEXT,
            last_synced_at TEXT,
            total_commits INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        -- Commits table
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            log_number INTEGER,
            commit_hash TEXT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            author_name TEXT,
            author_email TEXT,
            date TEXT NOT NULL,
            files_changed INTEGER DEFAULT 0,
            lines_added INTEGER DEFAULT 0,
            lines_deleted INTEGER DEFAULT 0,
            full_content TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Servers table
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            host TEXT,
            ssh_alias TEXT,
            ssh_user TEXT,
            ssh_port INTEGER DEFAULT 22,
            region TEXT,
            purpose TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        -- Deployments table
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            server_id INTEGER NOT NULL,
            environment TEXT NOT NULL,
            url TEXT,
            docker_compose TEXT,
            deploy_method TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        );

        -- Cloudflare tunnels table
        CREATE TABLE IF NOT EXISTS cloudflare_tunnels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tunnel_id TEXT NOT NULL,
            tunnel_name TEXT,
            hostname TEXT NOT NULL,
            service_url TEXT NOT NULL,
            project_id INTEGER,
            environment TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_commits_project_id ON commits(project_id);
        CREATE INDEX IF NOT EXISTS idx_commits_date ON commits(date DESC);
        CREATE INDEX IF NOT EXISTS idx_commits_type ON commits(type);
        CREATE INDEX IF NOT EXISTS idx_commits_title ON commits(title);
        CREATE INDEX IF NOT EXISTS idx_commits_project_date ON commits(project_id, date DESC);
        CREATE INDEX IF NOT EXISTS idx_deployments_project ON deployments(project_id);
        CREATE INDEX IF NOT EXISTS idx_deployments_server ON deployments(server_id);
        CREATE INDEX IF NOT EXISTS idx_tunnels_project ON cloudflare_tunnels(project_id);
        CREATE INDEX IF NOT EXISTS idx_servers_provider ON servers(provider);
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

def migrate_db():
    """Add new columns to existing tables (safe migration)"""
    conn = sqlite3.connect(DB_PATH)
    migrations = [
        "ALTER TABLE projects ADD COLUMN domain TEXT",
        "ALTER TABLE projects ADD COLUMN local_path TEXT",
        "ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'active'",
    ]
    for sql in migrations:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    migrate_db()
