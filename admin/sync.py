#!/usr/bin/env python3
"""
Sync dev-logs.json to SQLite database
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "devlog.db"

def load_config():
    """Load config.json"""
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def sync_project(conn, project_config):
    """Sync single project to database"""
    slug = project_config["slug"]
    name = project_config["name"]
    json_path = Path(project_config["json_path"]).expanduser()

    # Load JSON data if available
    logs = []
    if not json_path.exists():
        print(f"  [INFO] {name}: No dev-log JSON at {json_path} (metadata only)")
    else:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logs = data.get("logs", [])
        except Exception as e:
            print(f"  [ERROR] {name}: Failed to load JSON - {e}")

    # Insert or update project (always, regardless of JSON existence)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (slug, name, description, repository_url, tech_stack, html_url, total_commits, domain, local_path, status, last_synced_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            description = excluded.description,
            repository_url = excluded.repository_url,
            tech_stack = excluded.tech_stack,
            html_url = excluded.html_url,
            total_commits = excluded.total_commits,
            domain = excluded.domain,
            local_path = excluded.local_path,
            status = excluded.status,
            last_synced_at = datetime('now'),
            updated_at = datetime('now')
    """, (
        slug,
        name,
        project_config.get("description"),
        project_config.get("repository_url"),
        json.dumps(project_config.get("tech_stack", [])),
        project_config.get("html_url"),
        len(logs),
        project_config.get("domain"),
        project_config.get("local_path"),
        project_config.get("status", "active")
    ))

    # Get project ID
    project_id = cursor.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()[0]

    # Delete existing commits for clean sync
    cursor.execute("DELETE FROM commits WHERE project_id = ?", (project_id,))

    # Insert commits
    for log in logs:
        cursor.execute("""
            INSERT INTO commits (
                project_id, log_number, commit_hash, type, title,
                author_name, author_email, date,
                files_changed, lines_added, lines_deleted, full_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            log.get("log_number"),
            log.get("commit"),
            log.get("type", "feat"),
            log.get("title", "Untitled"),
            log.get("author", {}).get("name") if isinstance(log.get("author"), dict) else log.get("author"),
            log.get("author", {}).get("email") if isinstance(log.get("author"), dict) else None,
            log.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            log.get("files_changed", 0),
            log.get("lines_added", 0),
            log.get("lines_deleted", 0),
            log.get("full_content", "")
        ))

    conn.commit()
    print(f"  [OK] {name}: {len(logs)} commits synced")
    return len(logs)

def sync_servers(conn, servers_config):
    """Sync server inventory to database"""
    cursor = conn.cursor()
    for server in servers_config:
        cursor.execute("""
            INSERT INTO servers (slug, name, provider, host, ssh_alias, ssh_user, ssh_port, region, purpose, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                provider = excluded.provider,
                host = excluded.host,
                ssh_alias = excluded.ssh_alias,
                ssh_user = excluded.ssh_user,
                ssh_port = excluded.ssh_port,
                region = excluded.region,
                purpose = excluded.purpose,
                status = excluded.status,
                updated_at = datetime('now')
        """, (
            server["slug"], server["name"], server["provider"],
            server.get("host"), server.get("ssh_alias"),
            server.get("ssh_user"), server.get("ssh_port", 22),
            server.get("region"), server.get("purpose"),
            server.get("status", "active")
        ))
    conn.commit()
    print(f"  [OK] {len(servers_config)} servers synced")

def sync_deployments(conn, project_slug, deployments_config):
    """Sync deployment mappings for a project"""
    cursor = conn.cursor()
    project_row = cursor.execute("SELECT id FROM projects WHERE slug = ?", (project_slug,)).fetchone()
    if not project_row:
        return
    project_id = project_row[0]

    # Delete existing deployments for this project
    cursor.execute("DELETE FROM deployments WHERE project_id = ?", (project_id,))

    for dep in deployments_config:
        server_row = cursor.execute("SELECT id FROM servers WHERE slug = ?", (dep.get("server"),)).fetchone()
        if not server_row:
            continue
        server_id = server_row[0]
        cursor.execute("""
            INSERT INTO deployments (project_id, server_id, environment, url, docker_compose, deploy_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, server_id,
            dep.get("environment", "production"),
            dep.get("url"), dep.get("docker_compose"),
            dep.get("deploy_method", "docker"),
            dep.get("status", "active")
        ))
    conn.commit()

def sync_cloudflare_tunnels(conn, tunnels_config):
    """Sync Cloudflare tunnel data"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cloudflare_tunnels")

    for tunnel in tunnels_config:
        for route in tunnel.get("routes", []):
            project_row = cursor.execute(
                "SELECT id FROM projects WHERE slug = ?",
                (route.get("project_slug"),)
            ).fetchone()
            project_id = project_row[0] if project_row else None

            cursor.execute("""
                INSERT INTO cloudflare_tunnels (tunnel_id, tunnel_name, hostname, service_url, project_id, environment, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tunnel["tunnel_id"], tunnel.get("tunnel_name"),
                route["hostname"], route["service"],
                project_id, route.get("environment", "production"),
                "active"
            ))
    conn.commit()
    print(f"  [OK] {len(tunnels_config)} tunnels synced")

def main():
    """Main sync function"""
    from database import init_db, migrate_db
    init_db()
    migrate_db()

    config = load_config()
    conn = sqlite3.connect(DB_PATH)

    print("\n" + "="*60)
    print("Syncing dev-logs to SQLite")
    print("="*60 + "\n")

    # Sync servers first (deployments reference them)
    if "servers" in config:
        sync_servers(conn, config["servers"])

    # Sync projects and their deployments
    total_commits = 0
    for project in config["projects"]:
        commits = sync_project(conn, project)
        total_commits += commits
        # Sync deployments per project
        if "deployments" in project:
            sync_deployments(conn, project["slug"], project["deployments"])

    # Sync tunnels
    if "cloudflare_tunnels" in config:
        sync_cloudflare_tunnels(conn, config["cloudflare_tunnels"])

    conn.close()

    print("\n" + "="*60)
    print(f"Sync complete: {len(config['projects'])} projects, {total_commits} commits")
    if "servers" in config:
        print(f"  {len(config['servers'])} servers")
    if "cloudflare_tunnels" in config:
        print(f"  {len(config['cloudflare_tunnels'])} tunnels")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
