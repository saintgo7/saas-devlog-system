#!/usr/bin/env python3
"""
Auto-scan development environment to update config.json
Scans: SSH config, Cloudflare config, project directories
"""
import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(__file__).parent / "config.json"
SSH_CONFIG = Path.home() / ".ssh" / "config"
CLOUDFLARE_CONFIG = Path.home() / ".cloudflared" / "config.yml"
DEV_BASE = Path.home() / "01_DEV"


def scan_ssh_config():
    """Parse ~/.ssh/config for server entries"""
    servers = []
    if not SSH_CONFIG.exists():
        return servers

    current = {}
    with open(SSH_CONFIG) as f:
        for line in f:
            line = line.strip()
            if line.startswith("Host ") and not line.startswith("Host *"):
                if current and current.get("slug") != "github.com":
                    servers.append(current)
                host_alias = line.split()[1]
                current = {"slug": host_alias, "ssh_alias": host_alias}
            elif line.startswith("HostName"):
                hostname = line.split()[1]
                current["host"] = hostname
                # Auto-detect provider
                if "ec2" in hostname or "amazonaws" in hostname:
                    current["provider"] = "aws"
                    current["region"] = "ap-northeast-1"
                elif hostname.startswith("61.245"):
                    current["provider"] = "abada-onprem"
                    current["region"] = "seoul"
                else:
                    current["provider"] = "other"
            elif line.startswith("User"):
                current["ssh_user"] = line.split()[1]
            elif line.startswith("Port"):
                current["ssh_port"] = int(line.split()[1])

    if current and current.get("slug") != "github.com":
        servers.append(current)

    # Add default values
    for s in servers:
        s.setdefault("name", f"Server {s['slug']}")
        s.setdefault("provider", "other")
        s.setdefault("ssh_port", 22)
        s.setdefault("status", "active")
        s.setdefault("purpose", "")

    return servers


def scan_cloudflare_config():
    """Parse ~/.cloudflared/config.yml for tunnel entries"""
    tunnels = []
    if not CLOUDFLARE_CONFIG.exists():
        return tunnels

    try:
        import yaml
        with open(CLOUDFLARE_CONFIG) as f:
            config = yaml.safe_load(f)
    except ImportError:
        # Parse manually if yaml not available
        config = parse_cloudflare_yml(CLOUDFLARE_CONFIG)

    if not config:
        return tunnels

    tunnel_id = config.get("tunnel", "")
    routes = []
    for ingress in config.get("ingress", []):
        hostname = ingress.get("hostname")
        service = ingress.get("service")
        if hostname and service and service != "http_status:404":
            env = "staging" if "staging" in hostname else "production"
            routes.append({
                "hostname": hostname,
                "service": service,
                "environment": env
            })

    if routes:
        tunnels.append({
            "tunnel_id": tunnel_id,
            "tunnel_name": "auto-scanned",
            "routes": routes
        })

    return tunnels


def parse_cloudflare_yml(path):
    """Simple YAML parser for cloudflare config (no dependency)"""
    config = {"ingress": []}
    current_ingress = None

    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if stripped.startswith("tunnel:"):
                config["tunnel"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- hostname:"):
                if current_ingress:
                    config["ingress"].append(current_ingress)
                current_ingress = {"hostname": stripped.split(":", 1)[1].strip()}
            elif stripped.startswith("service:") and current_ingress is not None:
                current_ingress["service"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- service:"):
                if current_ingress:
                    config["ingress"].append(current_ingress)
                    current_ingress = None

    if current_ingress:
        config["ingress"].append(current_ingress)

    return config


def scan_projects(base_path):
    """Scan directory for git projects"""
    projects = []
    if not base_path.exists():
        return projects

    for item in sorted(base_path.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue

        # Check if it's a domain directory
        subdirs = [d for d in item.iterdir() if d.is_dir() and not d.name.startswith(".")]
        has_git = (item / ".git").exists()

        if has_git:
            # Direct project
            project = scan_single_project(item)
            if project:
                projects.append(project)
        else:
            # Possible domain directory - scan subdirectories
            for subdir in subdirs:
                if (subdir / ".git").exists():
                    project = scan_single_project(subdir, domain=item.name)
                    if project:
                        projects.append(project)

    return projects


def scan_single_project(path, domain=None):
    """Scan a single project directory"""
    project = {
        "slug": path.name,
        "name": path.name,
        "local_path": str(path),
        "domain": domain,
        "has_docker": (path / "docker-compose.yml").exists() or (path / "Dockerfile").exists(),
        "has_env": any(path.glob(".env*")),
        "status": "active"
    }

    # Get git remote
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(path), capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            project["repository_url"] = result.stdout.strip()
    except Exception:
        pass

    return project


def update_config(servers, tunnels, projects):
    """Merge scan results into config.json"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    else:
        config = {"projects": []}

    # Update servers
    existing_slugs = {s["slug"] for s in config.get("servers", [])}
    new_servers = [s for s in servers if s["slug"] not in existing_slugs]
    if new_servers:
        config.setdefault("servers", []).extend(new_servers)
        print(f"  Added {len(new_servers)} new servers")

    # Update tunnels
    if tunnels:
        config["cloudflare_tunnels"] = tunnels
        print(f"  Updated {len(tunnels)} tunnels")

    # Report new projects found
    existing_project_paths = {p.get("local_path") for p in config.get("projects", [])}
    new_projects = [p for p in projects if p["local_path"] not in existing_project_paths]
    if new_projects:
        print(f"  Found {len(new_projects)} new projects (not auto-added, review manually):")
        for p in new_projects[:10]:
            print(f"    - {p['local_path']}")

    return config


def main():
    print("\n" + "="*60)
    print("Scanning development environment")
    print("="*60 + "\n")

    print("[1/3] Scanning SSH config...")
    servers = scan_ssh_config()
    print(f"  Found {len(servers)} servers")

    print("[2/3] Scanning Cloudflare config...")
    tunnels = scan_cloudflare_config()
    print(f"  Found {len(tunnels)} tunnel configurations")

    print("[3/3] Scanning project directories...")
    projects = scan_projects(DEV_BASE)
    print(f"  Found {len(projects)} projects")

    print("\nUpdating config.json...")
    config = update_config(servers, tunnels, projects)

    # Write updated config
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nConfig saved to {CONFIG_PATH}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
