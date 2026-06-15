#!/usr/bin/env python3
"""
Dev Log Admin API Server - SQLite Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import sqlite3
import subprocess
import re
import mimetypes
from typing import Optional, List
from contextlib import contextmanager
from pathlib import Path
import json

app = FastAPI(title="Dev Log Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

DB_PATH = "devlog.db"
CONFIG_PATH = "config.json"


def _load_project_paths():
    """Load project paths from config.json, mapping slug -> directory path"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        paths = {}
        for p in config.get("projects", []):
            json_path = str(Path(p["json_path"]).expanduser())
            proj_dir = json_path.replace("/docs/html/data/dev-logs.json", "").replace("/Docs/html/data/dev-logs.json", "")
            paths[p["slug"]] = proj_dir
        return paths
    except Exception:
        return {}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Return proper JSON for unhandled errors"""
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ==========================================
# Deployment Scanning Functions
# ==========================================

GIT_PATH = "/usr/bin/git"

PLATFORM_FILES = {
    "vercel.json": "Vercel",
    ".vercel": "Vercel",
    "wrangler.toml": "Cloudflare",
    "wrangler.jsonc": "Cloudflare",
    "netlify.toml": "Netlify",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker",
    "docker-compose.yaml": "Docker",
    "fly.toml": "Fly.io",
    "CNAME": "GitHub Pages",
    "firebase.json": "Firebase",
    "app.yaml": "Google Cloud",
    "render.yaml": "Render",
}


def _detect_platforms(path: Path) -> list:
    """Detect deployment platforms by checking config files"""
    found = set()
    for filename, platform in PLATFORM_FILES.items():
        if (path / filename).exists():
            found.add(platform)
    return sorted(found)


def _detect_cicd(path: Path) -> dict:
    """Detect CI/CD workflows from .github/workflows/"""
    workflows_dir = path / ".github" / "workflows"
    result = {"workflows": [], "has_ci": False}
    if not workflows_dir.is_dir():
        return result

    for f in sorted(workflows_dir.iterdir()):
        if f.suffix not in (".yml", ".yaml"):
            continue
        name = f.stem
        # Classify workflow type
        name_lower = name.lower()
        if any(k in name_lower for k in ("deploy", "release", "publish", "cd")):
            wf_type = "deploy"
        elif any(k in name_lower for k in ("test", "spec", "e2e")):
            wf_type = "test"
        else:
            wf_type = "ci"
        result["workflows"].append({"name": name, "file": f.name, "type": wf_type})

    result["has_ci"] = len(result["workflows"]) > 0
    return result


def _extract_domains(path: Path, platforms: list, cicd: dict) -> list:
    """Extract domain names from config files and workflows"""
    domains = set()

    # CNAME file (GitHub Pages)
    cname = path / "CNAME"
    if cname.is_file():
        try:
            content = cname.read_text().strip()
            if content:
                domains.add(content)
        except Exception:
            pass

    # vercel.json
    vercel_json = path / "vercel.json"
    if vercel_json.is_file():
        try:
            data = json.loads(vercel_json.read_text())
            for alias in data.get("alias", []):
                domains.add(alias)
        except Exception:
            pass

    # wrangler.toml
    wrangler = path / "wrangler.toml"
    if wrangler.is_file():
        try:
            content = wrangler.read_text()
            for match in re.findall(r'(?:route|pattern)\s*=\s*["\']([^"\']+)', content):
                # Extract domain from route pattern like "example.com/*"
                domain = match.split("/")[0].replace("*.", "")
                if "." in domain:
                    domains.add(domain)
        except Exception:
            pass

    # Scan workflow files for domain hints
    workflows_dir = path / ".github" / "workflows"
    if workflows_dir.is_dir():
        for wf in cicd.get("workflows", []):
            wf_path = workflows_dir / wf["file"]
            try:
                content = wf_path.read_text()
                # Look for URL-like patterns in env vars
                for match in re.findall(r'https?://([a-zA-Z0-9][-a-zA-Z0-9.]+\.[a-zA-Z]{2,})', content):
                    excluded = (
                        "github.com", "githubusercontent.com", "npmjs.org",
                        "docker.io", "docker.com", "ghcr.io",
                        "python.org", "pytorch.org", "apple.com",
                        "google.com", "googleapis.com", "golang.org",
                        "cloudflare.com", "npmjs.com", "yarnpkg.com",
                        "k6.io", "grafana.com", "sentry.io",
                        "codecov.io", "coveralls.io", "sonarcloud.io",
                        "slack.com", "discord.com", "telegram.org",
                    )
                    if not any(x in match for x in excluded):
                        domains.add(match)
            except Exception:
                pass

    return sorted(domains)


def _get_git_status(proj_dir: str) -> dict:
    """Get git repository status"""
    result = {
        "current_branch": None,
        "uncommitted_count": 0,
        "branches": [],
        "ahead": 0,
        "behind": 0,
        "last_commit": None,
        "remote_url": None,
    }

    path = Path(proj_dir)
    if not (path / ".git").exists():
        return result

    def _run_git(*args):
        try:
            proc = subprocess.run(
                [GIT_PATH] + list(args),
                cwd=proj_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return proc.stdout.strip() if proc.returncode == 0 else ""
        except Exception:
            return ""

    # Current branch
    result["current_branch"] = _run_git("rev-parse", "--abbrev-ref", "HEAD") or None

    # Uncommitted changes count
    status_out = _run_git("status", "--porcelain")
    if status_out:
        result["uncommitted_count"] = len(status_out.splitlines())

    # Branches
    branches_out = _run_git("branch", "--format=%(refname:short)")
    if branches_out:
        result["branches"] = branches_out.splitlines()

    # Ahead/behind
    ab_out = _run_git("rev-list", "--left-right", "--count", "HEAD...@{upstream}")
    if ab_out:
        parts = ab_out.split()
        if len(parts) == 2:
            result["ahead"] = int(parts[0])
            result["behind"] = int(parts[1])

    # Last commit
    log_out = _run_git("log", "-1", "--format=%H|%s|%ai|%an")
    if log_out and "|" in log_out:
        parts = log_out.split("|", 3)
        if len(parts) == 4:
            result["last_commit"] = {
                "hash": parts[0][:8],
                "message": parts[1],
                "date": parts[2],
                "author": parts[3],
            }

    # Remote URL
    result["remote_url"] = _run_git("remote", "get-url", "origin") or None

    return result


def _scan_deployment_info(proj_dir: str) -> dict:
    """Scan project directory for deployment and git information"""
    path = Path(proj_dir)
    platforms = _detect_platforms(path)
    cicd = _detect_cicd(path)
    domains = _extract_domains(path, platforms, cicd)
    git_status = _get_git_status(proj_dir)

    return {
        "platforms": platforms,
        "ci_cd": cicd,
        "domains": domains,
        "git_status": git_status,
    }


# ==========================================
# Preview Detection Functions
# ==========================================

PREVIEW_ENTRY_POINTS = [
    {"type": "website", "label": "Project Website", "subpath": "frontend/dist", "priority": 1},
    {"type": "website", "label": "Project Website", "subpath": "",              "priority": 2},
    {"type": "devlog",  "label": "DevLog Dashboard", "subpath": "docs/html",    "priority": 3},
]


def _detect_preview_entry_points(proj_dir: str, slug: str) -> list:
    """Detect available preview entry points for a project"""
    path = Path(proj_dir)
    previews = []
    for ep in PREVIEW_ENTRY_POINTS:
        entry_dir = path / ep["subpath"] if ep["subpath"] else path
        if (entry_dir / "index.html").is_file():
            subpath = ep["subpath"]
            url = f"/preview/{slug}/{subpath}/" if subpath else f"/preview/{slug}/"
            previews.append({
                "type": ep["type"],
                "label": ep["label"],
                "subpath": subpath,
                "priority": ep["priority"],
                "url": url,
            })
    return sorted(previews, key=lambda x: x["priority"])


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

@app.get("/api/projects/deployment-badges")
def get_deployment_badges():
    """Get lightweight deployment badge data for all projects"""
    paths = _load_project_paths()
    badges = {}
    for slug, proj_dir in paths.items():
        path = Path(proj_dir)
        if not path.is_dir():
            continue
        platforms = _detect_platforms(path)
        has_ci = (path / ".github" / "workflows").is_dir() and any(
            f.suffix in (".yml", ".yaml") for f in (path / ".github" / "workflows").iterdir()
        ) if (path / ".github" / "workflows").is_dir() else False
        badges[slug] = {"platforms": platforms, "has_ci": has_ci}
    return badges

@app.get("/api/projects/preview-badges")
def get_preview_badges():
    """Get lightweight preview availability data for all projects (dashboard)"""
    paths = _load_project_paths()
    badges = {}
    thumbnails_dir = Path(__file__).parent / "static" / "thumbnails"
    for slug, proj_dir in paths.items():
        if not Path(proj_dir).is_dir():
            continue
        previews = _detect_preview_entry_points(proj_dir, slug)
        has_preview = len(previews) > 0
        preview_types = list({p["type"] for p in previews})
        primary_url = previews[0]["url"] if previews else None
        # Check thumbnail
        has_thumbnail = False
        thumbnail_url = None
        for ext in (".png", ".jpg", ".webp"):
            if (thumbnails_dir / f"{slug}{ext}").is_file():
                has_thumbnail = True
                thumbnail_url = f"/thumbnails/{slug}{ext}"
                break
        badges[slug] = {
            "has_preview": has_preview,
            "preview_types": preview_types,
            "has_thumbnail": has_thumbnail,
            "thumbnail_url": thumbnail_url,
            "primary_preview_url": primary_url,
        }
    return badges


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

@app.get("/api/projects/{slug}/deployment-info")
def get_deployment_info(slug: str):
    """Get detailed deployment and git status for a project"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    return _scan_deployment_info(proj_dir)

@app.get("/api/projects/{slug}/preview-info")
def get_preview_info(slug: str):
    """Get preview entry points for a specific project"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    previews = _detect_preview_entry_points(proj_dir, slug)
    thumbnails_dir = Path(__file__).parent / "static" / "thumbnails"
    has_thumbnail = False
    thumbnail_url = None
    for ext in (".png", ".jpg", ".webp"):
        if (thumbnails_dir / f"{slug}{ext}").is_file():
            has_thumbnail = True
            thumbnail_url = f"/thumbnails/{slug}{ext}"
            break
    return {
        "slug": slug,
        "previews": previews,
        "has_thumbnail": has_thumbnail,
        "thumbnail_url": thumbnail_url,
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

@app.delete("/api/projects/{slug}")
def delete_project(slug: str):
    """Delete a project and all its commits"""
    with get_db() as conn:
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_id = project["id"]
        conn.execute("DELETE FROM commits WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()

        return {"message": "Project deleted", "slug": slug}


@app.get("/api/projects/{slug}/path")
def get_project_path(slug: str):
    """Get project filesystem path"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    return {"slug": slug, "path": proj_dir}


@app.post("/api/projects/{slug}/open-folder")
def open_project_folder(slug: str):
    """Open project folder in Finder"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    subprocess.Popen(["open", proj_dir])
    return {"message": "Folder opened", "path": proj_dir}


@app.post("/api/projects/{slug}/open-terminal")
def open_project_terminal(slug: str):
    """Open project folder in Terminal"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    subprocess.Popen(["open", "-a", "Terminal", proj_dir])
    return {"message": "Terminal opened", "path": proj_dir}


@app.post("/api/projects/{slug}/open-vscode")
def open_project_vscode(slug: str):
    """Open project folder in VSCode"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    subprocess.Popen(["/usr/local/bin/code", proj_dir])
    return {"message": "VSCode opened", "path": proj_dir}


@app.post("/api/projects/{slug}/open-cursor")
def open_project_cursor(slug: str):
    """Open project folder in Cursor"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir or not Path(proj_dir).is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    subprocess.Popen(["/usr/local/bin/cursor", proj_dir])
    return {"message": "Cursor opened", "path": proj_dir}


@app.post("/api/sync")
def trigger_sync():
    """Trigger sync from config.json"""
    from sync import run_sync
    result = run_sync()
    return {
        "message": "Sync complete",
        "projects_synced": result["projects_synced"],
        "total_commits": result["total_commits"]
    }


@app.get("/api/projects/{slug}/stats")
def get_project_stats(slug: str):
    """Get per-project statistics"""
    with get_db() as conn:
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_id = project["id"]

        # Commits by type
        type_rows = conn.execute("""
            SELECT type, COUNT(*) as count
            FROM commits WHERE project_id = ?
            GROUP BY type ORDER BY count DESC
        """, (project_id,)).fetchall()
        commits_by_type = {row["type"]: row["count"] for row in type_rows}

        # Commits by month (last 6 months)
        month_rows = conn.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
            FROM commits
            WHERE project_id = ? AND date >= date('now', '-6 months')
            GROUP BY month ORDER BY month
        """, (project_id,)).fetchall()
        commits_by_month = {row["month"]: row["count"] for row in month_rows}

        # Totals
        totals = conn.execute("""
            SELECT
                COALESCE(SUM(lines_added), 0) as total_lines_added,
                COALESCE(SUM(lines_deleted), 0) as total_lines_deleted,
                COALESCE(SUM(files_changed), 0) as total_files_changed
            FROM commits WHERE project_id = ?
        """, (project_id,)).fetchone()

        # Most active day of week
        day_row = conn.execute("""
            SELECT
                CASE CAST(strftime('%w', date) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_name,
                COUNT(*) as count
            FROM commits WHERE project_id = ?
            GROUP BY strftime('%w', date)
            ORDER BY count DESC
            LIMIT 1
        """, (project_id,)).fetchone()

        return {
            "commits_by_type": commits_by_type,
            "commits_by_month": commits_by_month,
            "total_lines_added": totals["total_lines_added"],
            "total_lines_deleted": totals["total_lines_deleted"],
            "total_files_changed": totals["total_files_changed"],
            "most_active_day": day_row["day_name"] if day_row else None
        }


@app.get("/api/stats/activity-heatmap")
def get_activity_heatmap(days: int = 90):
    """Get activity heatmap data (daily commit counts)"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT date(date) as date, COUNT(*) as count
            FROM commits
            WHERE date >= date('now', '-' || ? || ' days')
            GROUP BY date(date)
            ORDER BY date
        """, (days,)).fetchall()

        return [{"date": row["date"], "count": row["count"]} for row in rows]


# ==========================================
# Preview Static File Serving
# ==========================================

@app.get("/preview/{slug}/{path:path}")
def serve_preview(slug: str, path: str = ""):
    """Serve project static files for preview"""
    paths = _load_project_paths()
    proj_dir = paths.get(slug)
    if not proj_dir:
        raise HTTPException(status_code=404, detail="Project not found")

    proj_path = Path(proj_dir).resolve()
    if not proj_path.is_dir():
        raise HTTPException(status_code=404, detail="Project directory not found")

    # Default to index.html for directory paths
    if not path or path.endswith("/"):
        path = path + "index.html" if path else "index.html"

    file_path = (proj_path / path).resolve()

    # Security: prevent path traversal (sibling-dir escape, ../ 등 차단)
    if not file_path.is_relative_to(proj_path):
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.is_file():
        # Try appending index.html for directory-like paths
        index_path = file_path / "index.html"
        if index_path.is_file():
            file_path = index_path
        else:
            raise HTTPException(status_code=404, detail="File not found")

    # Determine content type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"

    # For HTML files in frontend/dist, rewrite base href for correct asset loading
    if content_type == "text/html" and "frontend/dist" in str(file_path):
        try:
            html_content = file_path.read_text(encoding="utf-8")
            base_href = f"/preview/{slug}/frontend/dist/"
            # Insert or replace <base> tag
            if "<base " in html_content:
                html_content = re.sub(
                    r'<base\s+href="[^"]*"',
                    f'<base href="{base_href}"',
                    html_content,
                )
            elif "<head>" in html_content:
                html_content = html_content.replace(
                    "<head>",
                    f'<head><base href="{base_href}">',
                )
            # Rewrite root-absolute src/href paths
            html_content = re.sub(
                r'(src|href)="/assets/',
                f'\\1="{base_href}assets/',
                html_content,
            )
            return HTMLResponse(content=html_content)
        except Exception:
            pass

    return FileResponse(file_path, media_type=content_type)


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

# Mount static files (must be last)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Dev Log Admin Server")
    print("="*60)
    print("📊 Dashboard: http://localhost:8100")
    print("📖 API Docs:  http://localhost:8100/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8100)
