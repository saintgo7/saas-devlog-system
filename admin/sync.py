#!/usr/bin/env python3
"""
Sync dev-logs.json to SQLite database
"""
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "devlog.db"

# Conventional commit types
COMMIT_TYPES = {"feat", "fix", "docs", "style", "refactor", "perf", "test",
                "chore", "ci", "build", "revert", "hotfix", "feature", "setup"}


def parse_full_content(content):
    """Parse full_content markdown to extract title, type, date, author, commit hash, and stats."""
    result = {
        "title": None,
        "type": None,
        "date": None,
        "author_name": None,
        "commit": None,
        "files_changed": 0,
        "lines_added": 0,
        "lines_deleted": 0,
    }
    if not content:
        return result

    lines = content.split("\n")

    # Extract title from first heading
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            raw_title = line[2:].strip()
            # Pattern: "개발 로그 #NN - 제목" or "Dev Log #NNN: 제목"
            m = re.match(r"(?:개발 로그|Dev Log)\s*#?\d+\s*[-:]\s*(.+)", raw_title)
            if m:
                raw_title = m.group(1).strip()
            # Pattern: "개발 로그: type: 제목"
            m2 = re.match(r"개발 로그:\s*(.+)", raw_title)
            if m2:
                raw_title = m2.group(1).strip()
            result["title"] = raw_title
            break

    # Extract type from metadata line "**타입**: xxx" or "**Type**: xxx"
    type_match = re.search(r"\*\*(?:타입|Type|작업 유형)\*\*:\s*(\S+)", content)
    if type_match:
        t = type_match.group(1).strip().lower()
        if t in COMMIT_TYPES:
            result["type"] = t

    # If no type from metadata, try extracting from title prefix "feat: ...", "fix(scope): ..."
    if not result["type"] and result["title"]:
        m = re.match(r"(\w+)(?:\([^)]*\))?:\s*(.+)", result["title"])
        if m and m.group(1).lower() in COMMIT_TYPES:
            result["type"] = m.group(1).lower()
            result["title"] = m.group(2).strip()

    # Extract date: "**날짜**: 2026-01-02 04:40" or "**Date**: 2026-01-20 10:00"
    date_match = re.search(r"\*\*(?:날짜|Date|생성일시)\*\*:\s*(.+)", content)
    if date_match:
        raw_date = date_match.group(1).strip()
        # Handle Korean date format: "2026년 01월 02일 19:49:08"
        km = re.match(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*([\d:]+)", raw_date)
        if km:
            raw_date = f"{km.group(1)}-{km.group(2).zfill(2)}-{km.group(3).zfill(2)} {km.group(4)}"
        result["date"] = raw_date

    # Extract author: "**작업자**: xxx" or "**Author**: xxx" or "**작성자**: xxx"
    author_match = re.search(r"\*\*(?:작업자|Author|작성자)\*\*:\s*(.+)", content)
    if author_match:
        author = author_match.group(1).strip()
        # Clean email format: "saintgo7 <email>" -> "saintgo7"
        author = re.sub(r"\s*<[^>]+>", "", author)
        result["author_name"] = author

    # Extract commit hash: "**커밋**: abc123" or "**해시**: abc123"
    commit_match = re.search(r"\*\*(?:커밋|해시|Commit)\*\*:\s*`?([a-f0-9]{6,40})`?", content)
    if commit_match:
        result["commit"] = commit_match.group(1)

    # Extract stats from table: "| 변경된 파일 | 69개 |", "| 추가된 라인 | +9285 |"
    files_match = re.search(r"변경된 파일\s*\|\s*(\d+)", content)
    if files_match:
        result["files_changed"] = int(files_match.group(1))
    added_match = re.search(r"추가된 라인\s*\|\s*\+?(\d+)", content)
    if added_match:
        result["lines_added"] = int(added_match.group(1))
    deleted_match = re.search(r"삭제된 라인\s*\|\s*-?(\d+)", content)
    if deleted_match:
        result["lines_deleted"] = int(deleted_match.group(1))

    return result


def load_config():
    """Load config.json"""
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def sync_project(conn, project_config):
    """Sync single project to database"""
    slug = project_config["slug"]
    name = project_config["name"]
    json_path = Path(project_config["json_path"]).expanduser()

    if not json_path.exists():
        print(f"⚠️  [SKIP] {name}: JSON not found at {json_path}")
        return 0

    # Load JSON data
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ [ERROR] {name}: Failed to load JSON - {e}")
        return 0

    logs = data.get("logs", [])

    # Insert or update project
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (slug, name, description, repository_url, tech_stack, html_url, total_commits, last_synced_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            description = excluded.description,
            repository_url = excluded.repository_url,
            tech_stack = excluded.tech_stack,
            html_url = excluded.html_url,
            total_commits = excluded.total_commits,
            last_synced_at = datetime('now'),
            updated_at = datetime('now')
    """, (
        slug,
        name,
        project_config.get("description"),
        project_config.get("repository_url"),
        json.dumps(project_config.get("tech_stack", [])),
        project_config.get("html_url"),
        len(logs)
    ))

    # Get project ID
    project_id = cursor.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()[0]

    # Delete existing commits for clean sync
    cursor.execute("DELETE FROM commits WHERE project_id = ?", (project_id,))

    # Insert commits
    for log in logs:
        # Parse full_content for missing fields
        parsed = parse_full_content(log.get("full_content", ""))

        # Resolve each field: explicit log field > parsed from content > default
        log_number = log.get("log_number") or log.get("number")
        commit_hash = log.get("commit") or parsed["commit"]
        commit_type = log.get("type") or parsed["type"] or "feat"
        title = log.get("title") or parsed["title"] or "Untitled"

        if isinstance(log.get("author"), dict):
            author_name = log["author"].get("name")
            author_email = log["author"].get("email")
        else:
            author_name = log.get("author") or parsed["author_name"]
            author_email = None

        date = log.get("date") or parsed["date"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files_changed = log.get("files_changed") or parsed["files_changed"]
        lines_added = log.get("lines_added") or parsed["lines_added"]
        lines_deleted = log.get("lines_deleted") or parsed["lines_deleted"]

        cursor.execute("""
            INSERT INTO commits (
                project_id, log_number, commit_hash, type, title,
                author_name, author_email, date,
                files_changed, lines_added, lines_deleted, full_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, log_number, commit_hash, commit_type, title,
            author_name, author_email, date,
            files_changed, lines_added, lines_deleted,
            log.get("full_content", "")
        ))

    conn.commit()
    print(f"✅ [OK] {name}: {len(logs)} commits synced")
    return len(logs)

def run_sync():
    """Run sync and return results. Can be called from server.py or standalone."""
    config = load_config()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")

    total_commits = 0
    projects_synced = 0
    for project in config["projects"]:
        commits = sync_project(conn, project)
        total_commits += commits
        if commits > 0:
            projects_synced += 1

    # Clean up projects not in config
    config_slugs = {p["slug"] for p in config["projects"]}
    if config_slugs:
        conn.execute(
            "DELETE FROM projects WHERE slug NOT IN ({})".format(
                ",".join("?" * len(config_slugs))
            ),
            list(config_slugs)
        )
        conn.commit()

    conn.close()
    return {"projects_synced": projects_synced, "total_commits": total_commits}


def main():
    """Main entry point for standalone usage"""
    print("\n" + "="*60)
    print("Syncing dev-logs to SQLite")
    print("="*60 + "\n")

    result = run_sync()

    print("\n" + "="*60)
    print(f"Sync complete: {result['projects_synced']} projects, {result['total_commits']} commits")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
