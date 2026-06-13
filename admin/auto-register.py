#!/usr/bin/env python3
"""
Auto-register projects from ~/01_DEV into config.json and sync to DB.

Scans ~/01_DEV for directories containing docs/html/data/dev-logs.json
and adds any new ones to config.json automatically.

Can also register directories without dev-logs.json (with --all flag)
so they appear in the dashboard as empty projects ready for setup.

Usage:
    python3 auto-register.py          # only projects with dev-logs.json
    python3 auto-register.py --all    # all directories (including empty)
    python3 auto-register.py --dry-run  # preview without changes
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEV_DIR = Path.home() / "01_DEV"
ADMIN_DIR = Path(__file__).parent
CONFIG_PATH = ADMIN_DIR / "config.json"

# Directories to skip (not real projects)
SKIP_DIRS = {
    "docs", "ETC", "01_Claude_Code", "development-misc",
    "24-archive", "09_HTML", "dev-search", "27_opencode",
}

# File patterns that indicate it's not a project directory
SKIP_PATTERNS = {".sln", ".md", ".log", ".txt", ".json"}


def slug_from_dirname(dirname):
    """Generate a URL-friendly slug from directory name."""
    slug = dirname.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    # Remove common prefixes like "25-", "26-"
    slug = re.sub(r"^\d{2}-", "", slug)
    return slug or dirname.lower()


def name_from_dirname(dirname):
    """Generate a human-readable name from directory name."""
    name = dirname
    # Remove numeric prefixes like "25-", "26-"
    name = re.sub(r"^\d{2}[-_]", "", name)
    # Replace separators with spaces
    name = name.replace("-", " ").replace("_", " ")
    # Title case
    name = name.title()
    return name


def detect_tech_stack(project_dir):
    """Detect tech stack from project files."""
    tech = []
    files = {f.name for f in project_dir.iterdir() if f.is_file()}
    dirs = {d.name for d in project_dir.iterdir() if d.is_dir()}

    if "package.json" in files:
        try:
            pkg = json.loads((project_dir / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                tech.append("Next.js")
            if "react" in deps:
                tech.append("React")
            if "react-native" in deps:
                tech.append("React Native")
            if "vue" in deps:
                tech.append("Vue")
            if "svelte" in deps:
                tech.append("Svelte")
            if "express" in deps:
                tech.append("Express")
            if "typescript" in deps:
                tech.append("TypeScript")
        except Exception:
            tech.append("Node.js")

    if "requirements.txt" in files or "pyproject.toml" in files or "Pipfile" in files:
        tech.append("Python")
    if "go.mod" in files:
        tech.append("Go")
    if "Cargo.toml" in files:
        tech.append("Rust")
    if "pubspec.yaml" in files:
        tech.append("Flutter")
    if any(f.endswith(".sln") or f.endswith(".csproj") for f in files):
        tech.append(".NET")
    if "Dockerfile" in files or "docker-compose.yml" in files:
        tech.append("Docker")

    return tech[:5] if tech else ["Unknown"]


def detect_git_remote(project_dir):
    """Get git remote URL if available."""
    try:
        result = subprocess.run(
            ["git", "-C", str(project_dir), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Convert SSH to HTTPS
            if url.startswith("git@github.com:"):
                url = url.replace("git@github.com:", "https://github.com/")
            if url.endswith(".git"):
                url = url[:-4]
            return url
    except Exception:
        pass
    return ""


def load_config():
    """Load existing config.json."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": []}


def save_config(config):
    """Save config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")


def scan_projects(include_all=False):
    """Scan ~/01_DEV for project directories."""
    if not DEV_DIR.is_dir():
        print(f"Error: {DEV_DIR} not found")
        return []

    projects = []
    for entry in sorted(DEV_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in SKIP_DIRS:
            continue
        if entry.name.startswith("."):
            continue

        devlog_json = entry / "docs" / "html" / "data" / "dev-logs.json"
        has_devlog = devlog_json.exists()

        if not include_all and not has_devlog:
            continue

        projects.append({
            "dir": entry,
            "has_devlog": has_devlog,
            "devlog_path": devlog_json,
        })

    return projects


def main():
    include_all = "--all" in sys.argv
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("Auto-Register: Scanning ~/01_DEV")
    print("=" * 60)

    config = load_config()
    existing_slugs = {p["slug"] for p in config["projects"]}
    # Map json_path -> slug for dedup by path
    existing_paths = set()
    for p in config["projects"]:
        expanded = str(Path(p["json_path"]).expanduser())
        existing_paths.add(expanded)

    scanned = scan_projects(include_all=include_all)
    new_count = 0

    for proj in scanned:
        proj_dir = proj["dir"]
        devlog_path = proj["devlog_path"]
        expanded_path = str(devlog_path)

        # Skip if already registered (by path)
        if expanded_path in existing_paths:
            continue

        slug = slug_from_dirname(proj_dir.name)
        # Avoid slug collision
        if slug in existing_slugs:
            slug = slug + "-2"

        name = name_from_dirname(proj_dir.name)
        tech = detect_tech_stack(proj_dir)
        repo_url = detect_git_remote(proj_dir)

        json_path_str = str(devlog_path).replace(str(Path.home()), "~")

        entry = {
            "slug": slug,
            "name": name,
            "description": "",
            "repository_url": repo_url,
            "tech_stack": tech,
            "html_url": "",
            "json_path": json_path_str,
        }

        status = "with devlog" if proj["has_devlog"] else "empty"
        print(f"  [NEW] {name} ({slug}) [{status}]")
        if repo_url:
            print(f"         repo: {repo_url}")
        if tech:
            print(f"         tech: {', '.join(tech)}")

        if not dry_run:
            config["projects"].append(entry)
            existing_slugs.add(slug)
            existing_paths.add(expanded_path)

        new_count += 1

    print()
    if new_count == 0:
        print("No new projects found.")
    elif dry_run:
        print(f"Found {new_count} new projects (dry-run, no changes saved)")
    else:
        save_config(config)
        print(f"Added {new_count} new projects to config.json")

        # Run sync
        print("\nRunning sync...")
        result = subprocess.run(
            [sys.executable, str(ADMIN_DIR / "sync.py")],
            cwd=str(ADMIN_DIR),
        )
        if result.returncode == 0:
            print("Sync complete.")
        else:
            print("Sync failed.")

    print("=" * 60)


if __name__ == "__main__":
    main()
