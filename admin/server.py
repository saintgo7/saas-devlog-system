#!/usr/bin/env python3
"""
Dev Log Admin API Server - SQLite Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
from typing import Optional, List
from contextlib import contextmanager
import json

app = FastAPI(title="Dev Log Admin API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DB_PATH = "devlog.db"

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ==========================================
# API Endpoints
# ==========================================

@app.get("/api/projects")
def list_projects():
    """Get all projects"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, slug, name, description, repository_url, tech_stack, html_url,
                   total_commits, last_synced_at
            FROM projects
            ORDER BY name
        """).fetchall()

        return [
            {
                "id": row["id"],
                "slug": row["slug"],
                "name": row["name"],
                "description": row["description"],
                "repository_url": row["repository_url"],
                "tech_stack": json.loads(row["tech_stack"]) if row["tech_stack"] else [],
                "html_url": row["html_url"],
                "total_commits": row["total_commits"],
                "last_synced_at": row["last_synced_at"]
            }
            for row in rows
        ]

@app.get("/api/projects/{slug}")
def get_project(slug: str):
    """Get project details"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT id, slug, name, description, repository_url, tech_stack, html_url,
                   total_commits, last_synced_at, created_at, updated_at
            FROM projects
            WHERE slug = ?
        """, (slug,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get type statistics for this project
        type_stats = conn.execute("""
            SELECT type, COUNT(*) as count
            FROM commits
            WHERE project_id = ?
            GROUP BY type
        """, (row["id"],)).fetchall()

        return {
            "id": row["id"],
            "slug": row["slug"],
            "name": row["name"],
            "description": row["description"],
            "repository_url": row["repository_url"],
            "tech_stack": json.loads(row["tech_stack"]) if row["tech_stack"] else [],
            "html_url": row["html_url"],
            "total_commits": row["total_commits"],
            "last_synced_at": row["last_synced_at"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "type_stats": {stat["type"]: stat["count"] for stat in type_stats}
        }

@app.get("/api/projects/{slug}/commits")
def get_project_commits(
    slug: str,
    limit: int = 50,
    offset: int = 0,
    type: Optional[str] = None,
    search: Optional[str] = None
):
    """Get commits for a project"""
    with get_db() as conn:
        # Get project ID
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_id = project["id"]

        # Build query
        query = """
            SELECT id, log_number, commit_hash, type, title, author_name, author_email,
                   date, files_changed, lines_added, lines_deleted
            FROM commits
            WHERE project_id = ?
        """
        params = [project_id]

        if type:
            query += " AND type = ?"
            params.append(type)

        if search:
            query += " AND (title LIKE ? OR full_content LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        # Get total count
        count_query = query.replace("SELECT id, log_number, commit_hash, type, title, author_name, author_email, date, files_changed, lines_added, lines_deleted", "SELECT COUNT(*)")
        total = conn.execute(count_query, params).fetchone()[0]

        # Add pagination
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "commits": [dict(row) for row in rows]
        }

@app.get("/api/commits/{commit_id}")
def get_commit_detail(commit_id: int):
    """Get full commit details including content"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT c.*, p.slug as project_slug, p.name as project_name
            FROM commits c
            JOIN projects p ON c.project_id = p.id
            WHERE c.id = ?
        """, (commit_id,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Commit not found")

        return dict(row)

@app.get("/api/search")
def search_commits(
    q: str,
    project: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Search commits across all projects"""
    with get_db() as conn:
        query = """
            SELECT c.id, c.log_number, c.commit_hash, c.type, c.title,
                   c.author_name, c.date, c.files_changed, c.lines_added, c.lines_deleted,
                   p.slug as project_slug, p.name as project_name
            FROM commits c
            JOIN projects p ON c.project_id = p.id
            WHERE (c.title LIKE ? OR c.full_content LIKE ?)
        """
        params = [f"%{q}%", f"%{q}%"]

        if project:
            query += " AND p.slug = ?"
            params.append(project)

        if type:
            query += " AND c.type = ?"
            params.append(type)

        # Count total
        count_query = query.replace(
            "SELECT c.id, c.log_number, c.commit_hash, c.type, c.title, c.author_name, c.date, c.files_changed, c.lines_added, c.lines_deleted, p.slug as project_slug, p.name as project_name",
            "SELECT COUNT(*)"
        )
        total = conn.execute(count_query, params).fetchone()[0]

        # Add pagination
        query += " ORDER BY c.date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "query": q,
            "results": [dict(row) for row in rows]
        }

@app.get("/api/stats/overview")
def get_overview_stats():
    """Get overall statistics"""
    with get_db() as conn:
        # Basic stats
        total_projects = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        total_commits = conn.execute("SELECT COUNT(*) as count FROM commits").fetchone()["count"]

        # Commits by type
        type_stats = conn.execute("""
            SELECT type, COUNT(*) as count
            FROM commits
            GROUP BY type
            ORDER BY count DESC
        """).fetchall()

        # Recent activity (last 20 commits)
        recent = conn.execute("""
            SELECT c.id, c.log_number, c.title, c.type, c.date,
                   p.slug as project_slug, p.name as project_name
            FROM commits c
            JOIN projects p ON c.project_id = p.id
            ORDER BY c.date DESC
            LIMIT 20
        """).fetchall()

        # Commits by project
        project_stats = conn.execute("""
            SELECT p.name, p.slug, COUNT(c.id) as commit_count
            FROM projects p
            LEFT JOIN commits c ON p.id = c.project_id
            GROUP BY p.id
            ORDER BY commit_count DESC
        """).fetchall()

        return {
            "total_projects": total_projects,
            "total_commits": total_commits,
            "commits_by_type": {stat["type"]: stat["count"] for stat in type_stats},
            "recent_activity": [dict(row) for row in recent],
            "commits_by_project": [dict(row) for row in project_stats]
        }

@app.get("/api/stats/timeline")
def get_timeline_stats(days: int = 30):
    """Get commit timeline statistics"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT
                date(date) as day,
                COUNT(*) as count,
                GROUP_CONCAT(DISTINCT type) as types
            FROM commits
            WHERE date >= date('now', '-' || ? || ' days')
            GROUP BY date(date)
            ORDER BY day DESC
        """, (days,)).fetchall()

        return {
            "days": days,
            "timeline": [dict(row) for row in rows]
        }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    with get_db() as conn:
        try:
            conn.execute("SELECT 1").fetchone()
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": str(e)}
            )

# ==========================================
# Infrastructure API Endpoints
# ==========================================

@app.get("/api/servers")
def list_servers(provider: Optional[str] = None):
    """List all servers, optionally filtered by provider"""
    with get_db() as conn:
        if provider:
            rows = conn.execute(
                "SELECT * FROM servers WHERE provider = ? ORDER BY name", (provider,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM servers ORDER BY provider, name").fetchall()

        return [dict(row) for row in rows]

@app.get("/api/servers/{slug}")
def get_server(slug: str):
    """Get server details with deployed projects"""
    with get_db() as conn:
        server = conn.execute("SELECT * FROM servers WHERE slug = ?", (slug,)).fetchone()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")

        # Get projects deployed on this server
        deployments = conn.execute("""
            SELECT d.*, p.slug as project_slug, p.name as project_name
            FROM deployments d
            JOIN projects p ON d.project_id = p.id
            WHERE d.server_id = ?
            ORDER BY p.name
        """, (server["id"],)).fetchall()

        result = dict(server)
        result["deployments"] = [dict(d) for d in deployments]
        return result

@app.get("/api/deployments")
def list_deployments(environment: Optional[str] = None):
    """List all deployments with project and server info"""
    with get_db() as conn:
        query = """
            SELECT d.*,
                   p.slug as project_slug, p.name as project_name, p.domain as project_domain,
                   s.slug as server_slug, s.name as server_name, s.provider as server_provider
            FROM deployments d
            JOIN projects p ON d.project_id = p.id
            JOIN servers s ON d.server_id = s.id
        """
        params = []
        if environment:
            query += " WHERE d.environment = ?"
            params.append(environment)
        query += " ORDER BY p.name, d.environment"

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/projects/{slug}/deployments")
def get_project_deployments(slug: str):
    """Get deployment info for a specific project"""
    with get_db() as conn:
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        deployments = conn.execute("""
            SELECT d.*, s.slug as server_slug, s.name as server_name,
                   s.provider as server_provider, s.host as server_host
            FROM deployments d
            JOIN servers s ON d.server_id = s.id
            WHERE d.project_id = ?
            ORDER BY d.environment
        """, (project["id"],)).fetchall()

        tunnels = conn.execute("""
            SELECT * FROM cloudflare_tunnels WHERE project_id = ?
        """, (project["id"],)).fetchall()

        return {
            "deployments": [dict(d) for d in deployments],
            "tunnels": [dict(t) for t in tunnels]
        }

@app.get("/api/tunnels")
def list_tunnels():
    """List all Cloudflare tunnels"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT ct.*, p.slug as project_slug, p.name as project_name
            FROM cloudflare_tunnels ct
            LEFT JOIN projects p ON ct.project_id = p.id
            ORDER BY ct.hostname
        """).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/stats/infrastructure")
def get_infrastructure_stats():
    """Get infrastructure overview statistics"""
    with get_db() as conn:
        total_servers = conn.execute("SELECT COUNT(*) as count FROM servers").fetchone()["count"]
        total_deployments = conn.execute("SELECT COUNT(*) as count FROM deployments").fetchone()["count"]
        total_tunnels = conn.execute("SELECT COUNT(*) as count FROM cloudflare_tunnels").fetchone()["count"]

        # Servers by provider
        providers = conn.execute("""
            SELECT provider, COUNT(*) as count
            FROM servers GROUP BY provider ORDER BY count DESC
        """).fetchall()

        # Deployments by environment
        environments = conn.execute("""
            SELECT environment, COUNT(*) as count
            FROM deployments GROUP BY environment ORDER BY count DESC
        """).fetchall()

        # Projects by domain
        domains = conn.execute("""
            SELECT domain, COUNT(*) as count
            FROM projects WHERE domain IS NOT NULL
            GROUP BY domain ORDER BY count DESC
        """).fetchall()

        return {
            "total_servers": total_servers,
            "total_deployments": total_deployments,
            "total_tunnels": total_tunnels,
            "servers_by_provider": {p["provider"]: p["count"] for p in providers},
            "deployments_by_environment": {e["environment"]: e["count"] for e in environments},
            "projects_by_domain": {d["domain"]: d["count"] for d in domains}
        }

# Mount static files (must be last)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("Dev Log Admin Server v2.0.0")
    print("  + Infrastructure Management APIs")
    print("="*60)
    print("Dashboard: http://localhost:8100")
    print("API Docs:  http://localhost:8100/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8100)
