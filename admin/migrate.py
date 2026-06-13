#!/usr/bin/env python3
"""
Safe incremental project migration script.
Moves projects to domain directories one at a time with verification.

Usage:
    python3 migrate.py --project saas-crew             # Migrate single project
    python3 migrate.py --domain 01_ABADA               # Migrate all in domain
    python3 migrate.py --domain 01_ABADA --dry-run     # Simulate only
    python3 migrate.py --status                        # Show migration status
    python3 migrate.py --verify                        # Re-verify all migrated
    python3 migrate.py --rollback saas-crew            # Rollback single project
    python3 migrate.py --audit                         # Git status audit
    python3 migrate.py --scan-paths                    # Scan hardcoded paths
    python3 migrate.py --cleanup-symlinks              # Remove all root symlinks
    python3 migrate.py --rename-domains                # Rename domain dirs
    python3 migrate.py --move-all --force-move         # Move all remaining
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
INVENTORY_PATH = Path.home() / "01_DEV" / "INVENTORY.json"
CONFIG_PATH = SCRIPT_DIR / "config.json"
MIGRATION_STATUS_PATH = Path.home() / "01_DEV" / "MIGRATION_STATUS.json"

# Projects that should NOT be moved (old_path == new_path)
SKIP_SLUGS = {"devlog-system", "devlog-admin"}

# Domain migration order (low risk -> high risk)
DOMAIN_ORDER = [
    "09_LEARNING", "10_MISC", "99_ARCHIVE", "07_WEB", "06_HEALTHCARE",
    "04_AI_BOT", "08_DEVTOOLS", "05_EMAIL",
    "03_TRAVEL", "02_ERP", "01_ABADA"
]

# Domain rename mapping (old -> new)
DOMAIN_RENAME_MAP = {
    "abada": "01_ABADA",
    "erp": "02_ERP",
    "travel": "03_TRAVEL",
    "ai-bot": "04_AI_BOT",
    "email": "05_EMAIL",
    "healthcare": "06_HEALTHCARE",
    "web": "07_WEB",
    "devtools": "08_DEVTOOLS",
    "learning": "09_LEARNING",
    "misc": "10_MISC",
    "_archive": "99_ARCHIVE",
}

# Reverse mapping (new -> old) for compatibility
DOMAIN_RENAME_REVERSE = {v: k for k, v in DOMAIN_RENAME_MAP.items()}

# Files to scan for hardcoded absolute paths
PATH_SCAN_PATTERNS = [
    ".env", ".env.*", ".env.local", ".env.production", ".env.development",
    "docker-compose.yml", "docker-compose.*.yml",
    ".claude/CLAUDE.md", "CLAUDE.md",
    "Makefile", "*.sh",
]


def load_inventory():
    """Load INVENTORY.json"""
    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inventory(data):
    """Save INVENTORY.json"""
    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    f.close()


def load_config():
    """Load config.json"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    """Save config.json"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log(level, msg):
    """Simple logger"""
    icons = {"OK": "[OK]", "WARN": "[WARN]", "ERR": "[ERR]", "INFO": "[INFO]", "SKIP": "[SKIP]", "DRY": "[DRY]"}
    prefix = icons.get(level, f"[{level}]")
    print(f"  {prefix} {msg}")


# =============================================================================
# Git Status Audit
# =============================================================================

def check_git_status(path):
    """Check git status for a project directory.
    Returns: 'CLEAN', 'DIRTY', or 'NO-GIT'
    """
    git_dir = Path(path) / ".git"
    if not git_dir.exists():
        return "NO-GIT"

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(path), capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return "NO-GIT"
        return "CLEAN" if not result.stdout.strip() else "DIRTY"
    except (subprocess.TimeoutExpired, Exception):
        return "NO-GIT"


def get_dirty_files(path):
    """Get list of uncommitted changes"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(path), capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")
    except Exception:
        pass
    return []


def audit_all_projects():
    """Run git status audit on all projects, generate MIGRATION_STATUS.json"""
    print("\n" + "=" * 60)
    print("Git Status Audit")
    print("=" * 60 + "\n")

    inventory = load_inventory()
    status_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": {"CLEAN": 0, "DIRTY": 0, "NO-GIT": 0, "MISSING": 0},
        "projects": []
    }

    for proj in inventory["projects"]:
        slug = proj["slug"]
        old_path = proj["old_path"]

        if slug in SKIP_SLUGS:
            log("SKIP", f"{slug}: skip project (stays in place)")
            continue

        if not Path(old_path).exists():
            # Check if already migrated
            new_path = proj["new_path"]
            if Path(new_path).exists():
                git_status = check_git_status(new_path)
                entry = {
                    "slug": slug,
                    "path": new_path,
                    "git_status": git_status,
                    "already_migrated": True,
                    "dirty_files": get_dirty_files(new_path) if git_status == "DIRTY" else []
                }
            else:
                status_data["summary"]["MISSING"] += 1
                entry = {"slug": slug, "path": old_path, "git_status": "MISSING", "dirty_files": []}
                log("WARN", f"{slug}: path not found ({old_path})")
                status_data["projects"].append(entry)
                continue
        else:
            git_status = check_git_status(old_path)
            entry = {
                "slug": slug,
                "path": old_path,
                "git_status": git_status,
                "already_migrated": False,
                "dirty_files": get_dirty_files(old_path) if git_status == "DIRTY" else []
            }

        status_data["summary"][git_status] = status_data["summary"].get(git_status, 0) + 1
        status_data["projects"].append(entry)

        icon = {"CLEAN": "OK", "DIRTY": "WARN", "NO-GIT": "INFO"}[git_status]
        log(icon, f"{slug}: {git_status}")

    # Save results
    with open(MIGRATION_STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)

    print(f"\n  Summary: {status_data['summary']}")
    print(f"  Saved to: {MIGRATION_STATUS_PATH}\n")
    return status_data


# =============================================================================
# Hardcoded Path Scanner
# =============================================================================

def scan_hardcoded_paths():
    """Scan all projects for files containing hardcoded absolute paths"""
    print("\n" + "=" * 60)
    print("Hardcoded Path Scanner")
    print("=" * 60 + "\n")

    inventory = load_inventory()
    results = {}
    search_pattern = "/Users/saint/01_DEV/"
    home_pattern = "/Users/saint/"

    for proj in inventory["projects"]:
        slug = proj["slug"]
        old_path = Path(proj["old_path"])
        check_path = old_path if old_path.exists() else Path(proj["new_path"])

        if not check_path.exists() or slug in SKIP_SLUGS:
            continue

        found_files = []

        # Scan specific file patterns
        for pattern in PATH_SCAN_PATTERNS:
            for match in check_path.glob(pattern):
                if match.is_file():
                    try:
                        content = match.read_text(encoding="utf-8", errors="ignore")
                        if search_pattern in content or (
                            home_pattern in content and str(check_path).startswith(str(Path.home()))
                            and not str(check_path).startswith(str(Path.home() / "01_DEV"))
                        ):
                            lines = []
                            for i, line in enumerate(content.split("\n"), 1):
                                if search_pattern in line or home_pattern in line:
                                    lines.append({"line": i, "content": line.strip()[:120]})
                            found_files.append({
                                "file": str(match.relative_to(check_path)),
                                "matches": lines
                            })
                    except Exception:
                        pass

        if found_files:
            results[slug] = found_files
            log("WARN", f"{slug}: {len(found_files)} file(s) with absolute paths")
        else:
            log("OK", f"{slug}: no hardcoded paths")

    # Save to MIGRATION_STATUS.json (append to existing if available)
    status_path = MIGRATION_STATUS_PATH
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            status_data = json.load(f)
    else:
        status_data = {}

    status_data["hardcoded_paths"] = results
    status_data["paths_scanned_at"] = datetime.now().isoformat()

    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)

    print(f"\n  {len(results)} project(s) with hardcoded paths")
    print(f"  Saved to: {status_path}\n")
    return results


# =============================================================================
# Pre-Check
# =============================================================================

def check_docker_running(path):
    """Check if Docker containers are running for a project"""
    compose_file = Path(path) / "docker-compose.yml"
    if not compose_file.exists():
        return False, []

    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=str(path), capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, result.stdout.strip().split("\n")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False, []


def pre_check(proj, dry_run=False, force=False):
    """Run pre-migration checks for a project.
    Returns (ok: bool, reason: str)
    """
    slug = proj["slug"]
    old_path = Path(proj["old_path"])
    new_path = Path(proj["new_path"])

    # Skip projects that stay in place
    if slug in SKIP_SLUGS:
        return False, "skip project (stays in place)"

    # Already migrated
    if proj.get("migrated", False):
        return False, "already migrated"

    # old_path == new_path means no move needed
    if str(old_path) == str(new_path):
        return False, "old_path == new_path, no move needed"

    # Source must exist
    if not old_path.exists():
        # Check if it's already at new_path (partial migration)
        if new_path.exists():
            return False, f"already at new_path (update inventory manually)"
        return False, f"source not found: {old_path}"

    # Destination parent must exist
    if not new_path.parent.exists():
        return False, f"destination parent missing: {new_path.parent}"

    # Destination must NOT exist (avoid overwrite)
    if new_path.exists():
        return False, f"destination already exists: {new_path}"

    # Check if source is a symlink (already has symlink from previous attempt)
    if old_path.is_symlink():
        return False, f"source is a symlink (possible partial migration)"

    # Git clean check (only for git repos) -- skip if force
    git_status = check_git_status(old_path)
    if git_status == "DIRTY" and not force:
        dirty = get_dirty_files(old_path)
        return False, f"DIRTY git status ({len(dirty)} uncommitted changes)"

    # Check Docker running
    if not dry_run:
        running, containers = check_docker_running(old_path)
        if running:
            return False, f"Docker containers running ({len(containers)} container(s))"

    return True, "OK"


# =============================================================================
# Migration (single project)
# =============================================================================

def migrate_single(proj, dry_run=False, force=False, create_symlink=False):
    """Migrate a single project: mv -> (optional symlink) -> verify -> record.
    Returns True on success.
    """
    slug = proj["slug"]
    old_path = Path(proj["old_path"])
    new_path = Path(proj["new_path"])

    print(f"\n  --- Migrating: {slug} ---")
    print(f"      From: {old_path}")
    print(f"      To:   {new_path}")

    # 1. Pre-check
    ok, reason = pre_check(proj, dry_run, force=force)
    if not ok:
        log("SKIP", f"{slug}: {reason}")
        return False

    if dry_run:
        log("DRY", f"{slug}: would move {old_path} -> {new_path}")
        if create_symlink:
            log("DRY", f"{slug}: would symlink {old_path} -> {new_path}")
        return True

    # 2. Move
    try:
        shutil.move(str(old_path), str(new_path))
        log("OK", f"Moved to {new_path}")
    except Exception as e:
        log("ERR", f"Move failed: {e}")
        return False

    # 3. Symlink (optional)
    if create_symlink:
        try:
            os.symlink(str(new_path), str(old_path))
            log("OK", f"Symlink created: {old_path} -> {new_path}")
        except Exception as e:
            log("WARN", f"Symlink failed: {e} (rolling back)")
            try:
                shutil.move(str(new_path), str(old_path))
                log("OK", f"Rollback successful: {old_path}")
            except Exception as e2:
                log("ERR", f"ROLLBACK FAILED: {e2} - MANUAL INTERVENTION NEEDED")
            return False

    # 4. Verify
    if not verify_single(proj, new_path):
        log("WARN", f"Verification failed, rolling back...")
        rollback_single(proj)
        return False

    # 5. Record
    proj["migrated"] = True
    log("OK", f"{slug}: migration complete")
    return True


def verify_single(proj, check_path=None):
    """Verify a migrated project.
    Returns True if all checks pass.
    """
    slug = proj["slug"]
    old_path = Path(proj["old_path"])
    new_path = Path(proj["new_path"])

    if check_path is None:
        check_path = new_path

    ok = True

    # new_path exists and has contents
    if not check_path.exists():
        log("ERR", f"{slug}: new_path does not exist")
        return False

    contents = list(check_path.iterdir())
    if not contents:
        log("WARN", f"{slug}: new_path is empty")
        # Empty directories are valid (some projects might be empty)

    # Symlink check (only if old_path != new_path)
    if str(old_path) != str(new_path):
        if old_path.is_symlink():
            target = os.readlink(str(old_path))
            if target != str(new_path):
                log("ERR", f"{slug}: symlink points to wrong target: {target}")
                ok = False
            else:
                log("OK", f"{slug}: symlink OK")
        else:
            # Symlink might not exist if it's a fresh verify
            pass

    # Git remote check
    git_dir = check_path / ".git"
    if git_dir.exists() and proj.get("git_remote"):
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=str(check_path), capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                log("OK", f"{slug}: git remote accessible")
            else:
                log("WARN", f"{slug}: git remote check failed")
        except Exception:
            log("WARN", f"{slug}: git remote check timeout")

    # Docker compose config check
    compose_file = check_path / "docker-compose.yml"
    if compose_file.exists():
        try:
            result = subprocess.run(
                ["docker", "compose", "config", "--quiet"],
                cwd=str(check_path), capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                log("OK", f"{slug}: docker compose config valid")
            else:
                log("WARN", f"{slug}: docker compose config issue")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            log("INFO", f"{slug}: docker not available for compose check")

    return ok


def rollback_single(proj):
    """Rollback a single project migration.
    Returns True on success.
    """
    slug = proj["slug"]
    old_path = Path(proj["old_path"])
    new_path = Path(proj["new_path"])

    print(f"\n  --- Rolling back: {slug} ---")

    # 1. Remove symlink at old_path
    if old_path.is_symlink():
        try:
            os.unlink(str(old_path))
            log("OK", f"Removed symlink: {old_path}")
        except Exception as e:
            log("ERR", f"Failed to remove symlink: {e}")
            return False

    # 2. Move back from new_path to old_path
    if new_path.exists():
        try:
            shutil.move(str(new_path), str(old_path))
            log("OK", f"Moved back: {new_path} -> {old_path}")
        except Exception as e:
            log("ERR", f"Move back failed: {e}")
            return False
    else:
        log("WARN", f"new_path does not exist: {new_path}")

    # 3. Update record
    proj["migrated"] = False
    log("OK", f"{slug}: rollback complete")
    return True


# =============================================================================
# Config/Inventory Update
# =============================================================================

def update_config_paths(slug, old_local_path, new_local_path):
    """Update config.json paths for a migrated project"""
    config = load_config()
    updated = False

    for proj in config.get("projects", []):
        if proj["slug"] != slug:
            continue

        old_expanded = str(Path(old_local_path).expanduser())
        new_expanded = str(Path(new_local_path).expanduser())
        old_tilde = old_expanded.replace(str(Path.home()), "~")
        new_tilde = new_expanded.replace(str(Path.home()), "~")

        # Update local_path
        if proj.get("local_path"):
            proj["local_path"] = new_tilde
            updated = True

        # Update json_path (handles both ~ and absolute forms)
        if proj.get("json_path"):
            proj["json_path"] = proj["json_path"].replace(
                old_tilde, new_tilde
            ).replace(old_expanded, new_expanded)

        # Update html_url (always absolute in file:// URLs)
        if proj.get("html_url"):
            proj["html_url"] = proj["html_url"].replace(old_expanded, new_expanded)

        break

    if updated:
        save_config(config)
    return updated


# =============================================================================
# Domain / Batch Operations
# =============================================================================

def migrate_domain(domain, dry_run=False, force=False):
    """Migrate all projects in a domain.
    Matches by domain field (supports both old and new domain names).
    """
    inventory = load_inventory()
    projects = [p for p in inventory["projects"]
                if p["domain"] == domain and p["slug"] not in SKIP_SLUGS]

    if not projects:
        print(f"\n  No projects found for domain: {domain}")
        return

    print(f"\n{'=' * 60}")
    print(f"  Migrating domain: {domain} ({len(projects)} projects)")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    if force:
        print(f"  Force: ENABLED (DIRTY git repos will be moved)")
    print(f"{'=' * 60}")

    success = 0
    skipped = 0
    failed = 0

    for proj in projects:
        result = migrate_single(proj, dry_run, force=force, create_symlink=False)
        if result:
            success += 1
            if not dry_run:
                update_config_paths(proj["slug"], proj["old_path"], proj["new_path"])
        else:
            ok, reason = pre_check(proj, dry_run, force=force)
            if not ok and "already migrated" in reason:
                skipped += 1
            elif not ok:
                skipped += 1
            else:
                failed += 1

    if not dry_run:
        save_inventory(inventory)

    print(f"\n  --- Domain {domain} Summary ---")
    print(f"  Success: {success}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print(f"{'=' * 60}\n")

    return {"success": success, "skipped": skipped, "failed": failed}


def migrate_project(slug, dry_run=False, force=False):
    """Migrate a single project by slug"""
    inventory = load_inventory()
    proj = next((p for p in inventory["projects"] if p["slug"] == slug), None)

    if not proj:
        print(f"\n  Project not found: {slug}")
        return False

    print(f"\n{'=' * 60}")
    print(f"  Migrating project: {slug}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    if force:
        print(f"  Force: ENABLED")
    print(f"{'=' * 60}")

    result = migrate_single(proj, dry_run, force=force, create_symlink=False)

    if result and not dry_run:
        update_config_paths(proj["slug"], proj["old_path"], proj["new_path"])
        save_inventory(inventory)

    return result


def rollback_project(slug):
    """Rollback a single project by slug"""
    inventory = load_inventory()
    proj = next((p for p in inventory["projects"] if p["slug"] == slug), None)

    if not proj:
        print(f"\n  Project not found: {slug}")
        return False

    if not proj.get("migrated", False):
        print(f"\n  Project not migrated: {slug}")
        return False

    print(f"\n{'=' * 60}")
    print(f"  Rolling back: {slug}")
    print(f"{'=' * 60}")

    result = rollback_single(proj)

    if result:
        # Revert config.json
        update_config_paths(proj["slug"], proj["new_path"], proj["old_path"])
        save_inventory(inventory)

    return result


# =============================================================================
# Cleanup Symlinks
# =============================================================================

def cleanup_symlinks():
    """Remove all symlinks in ~/01_DEV root directory."""
    base = Path.home() / "01_DEV"
    print(f"\n{'=' * 60}")
    print("  Cleanup Symlinks")
    print(f"{'=' * 60}\n")

    removed = 0
    for item in sorted(base.iterdir()):
        if item.is_symlink():
            target = os.readlink(str(item))
            try:
                os.unlink(str(item))
                log("OK", f"Removed symlink: {item.name} -> {target}")
                removed += 1
            except Exception as e:
                log("ERR", f"Failed to remove {item.name}: {e}")

    print(f"\n  Removed {removed} symlink(s)")
    print(f"{'=' * 60}\n")
    return removed


# =============================================================================
# Rename Domains
# =============================================================================

def rename_domains(dry_run=False):
    """Rename domain directories from lowercase to numbered uppercase format.
    Also updates INVENTORY.json and config.json paths.
    """
    base = Path.home() / "01_DEV"
    print(f"\n{'=' * 60}")
    print("  Rename Domain Directories")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'=' * 60}\n")

    # 1. Rename physical directories
    renamed = 0
    for old_name, new_name in DOMAIN_RENAME_MAP.items():
        old_dir = base / old_name
        new_dir = base / new_name
        if old_dir.exists() and old_dir.is_dir() and not old_dir.is_symlink():
            if new_dir.exists():
                log("WARN", f"Target already exists: {new_name}, skipping")
                continue
            if dry_run:
                log("DRY", f"Would rename: {old_name}/ -> {new_name}/")
            else:
                old_dir.rename(new_dir)
                log("OK", f"Renamed: {old_name}/ -> {new_name}/")
            renamed += 1
        elif new_dir.exists():
            log("INFO", f"Already renamed: {new_name}/")
        else:
            log("WARN", f"Source not found: {old_name}/")

    print(f"\n  Renamed {renamed} directories")

    # 2. Update INVENTORY.json
    inventory = load_inventory()

    # 2a. Update domains metadata keys
    old_domains = inventory.get("domains", {})
    new_domains = {}
    for old_name, new_name in DOMAIN_RENAME_MAP.items():
        if old_name in old_domains:
            new_domains[new_name] = old_domains[old_name]
    # Keep any domains not in the map
    for k, v in old_domains.items():
        if k not in DOMAIN_RENAME_MAP:
            new_domains[k] = v
    inventory["domains"] = new_domains

    # 2b. Add _archive domain metadata if missing
    if "99_ARCHIVE" not in inventory["domains"]:
        inventory["domains"]["99_ARCHIVE"] = {
            "description": "Archived projects",
            "color": "#9ca3af"
        }

    # 2c. Update each project's domain and new_path
    path_updates = 0
    for proj in inventory["projects"]:
        # Update domain field
        old_domain = proj["domain"]
        if old_domain in DOMAIN_RENAME_MAP:
            proj["domain"] = DOMAIN_RENAME_MAP[old_domain]

        # Update new_path: replace /01_DEV/{old}/ with /01_DEV/{new}/
        for old_name, new_name in DOMAIN_RENAME_MAP.items():
            old_segment = f"/01_DEV/{old_name}/"
            new_segment = f"/01_DEV/{new_name}/"
            if old_segment in proj.get("new_path", ""):
                proj["new_path"] = proj["new_path"].replace(old_segment, new_segment)
                path_updates += 1
                break

    if dry_run:
        log("DRY", f"Would update {path_updates} project paths in INVENTORY.json")
    else:
        save_inventory(inventory)
        log("OK", f"Updated {path_updates} project paths in INVENTORY.json")

    # 3. Update config.json
    config = load_config()
    config_updates = 0
    home = str(Path.home())

    for proj in config.get("projects", []):
        updated = False
        for old_name, new_name in DOMAIN_RENAME_MAP.items():
            # Replace in local_path (~ format)
            old_tilde = f"~/01_DEV/{old_name}/"
            new_tilde = f"~/01_DEV/{new_name}/"
            old_abs = f"{home}/01_DEV/{old_name}/"
            new_abs = f"{home}/01_DEV/{new_name}/"

            for field in ["local_path", "json_path", "html_url"]:
                val = proj.get(field, "")
                if old_tilde in val or old_abs in val:
                    proj[field] = val.replace(old_tilde, new_tilde).replace(old_abs, new_abs)
                    updated = True

        if updated:
            config_updates += 1

    if dry_run:
        log("DRY", f"Would update {config_updates} project paths in config.json")
    else:
        save_config(config)
        log("OK", f"Updated {config_updates} project paths in config.json")

    print(f"\n  Domain rename complete")
    print(f"{'=' * 60}\n")


# =============================================================================
# Move All Remaining
# =============================================================================

def move_all_remaining(force=False, dry_run=False):
    """Move all remaining unmigrated projects to their domain directories.
    No symlinks are created.
    """
    inventory = load_inventory()
    pending = [p for p in inventory["projects"]
               if not p.get("migrated", False)
               and p["slug"] not in SKIP_SLUGS
               and str(p["old_path"]) != str(p["new_path"])]

    print(f"\n{'=' * 60}")
    print(f"  Move All Remaining Projects ({len(pending)} pending)")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    if force:
        print(f"  Force: ENABLED (DIRTY git repos will be moved)")
    print(f"{'=' * 60}")

    success = 0
    skipped = 0
    failed = 0

    for proj in pending:
        result = migrate_single(proj, dry_run, force=force, create_symlink=False)
        if result:
            success += 1
            if not dry_run:
                update_config_paths(proj["slug"], proj["old_path"], proj["new_path"])
        else:
            ok, reason = pre_check(proj, dry_run, force=force)
            if not ok:
                skipped += 1
            else:
                failed += 1

    if not dry_run:
        save_inventory(inventory)

    print(f"\n  --- Move All Summary ---")
    print(f"  Success: {success}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print(f"{'=' * 60}\n")

    return {"success": success, "skipped": skipped, "failed": failed}


# =============================================================================
# Status & Verify
# =============================================================================

def show_status():
    """Show migration status for all projects"""
    inventory = load_inventory()

    print(f"\n{'=' * 60}")
    print("  Migration Status")
    print(f"{'=' * 60}\n")

    domains = {}
    for proj in inventory["projects"]:
        domain = proj["domain"]
        if domain not in domains:
            domains[domain] = {"migrated": 0, "pending": 0, "skip": 0, "projects": []}

        if proj["slug"] in SKIP_SLUGS or str(proj["old_path"]) == str(proj["new_path"]):
            domains[domain]["skip"] += 1
            status = "SKIP"
        elif proj.get("migrated", False):
            domains[domain]["migrated"] += 1
            status = "DONE"
        else:
            domains[domain]["pending"] += 1
            status = "PENDING"

        domains[domain]["projects"].append((proj["slug"], status))

    total_migrated = 0
    total_pending = 0
    total_skip = 0

    for domain in DOMAIN_ORDER:
        if domain not in domains:
            continue
        d = domains[domain]
        total_migrated += d["migrated"]
        total_pending += d["pending"]
        total_skip += d["skip"]

        bar_done = "#" * d["migrated"]
        bar_pend = "." * d["pending"]
        bar_skip = "-" * d["skip"]
        total = d["migrated"] + d["pending"] + d["skip"]
        pct = (d["migrated"] / max(total - d["skip"], 1)) * 100 if (total - d["skip"]) > 0 else 100

        print(f"  {domain:12s} [{bar_done}{bar_pend}{bar_skip}] {d['migrated']}/{total - d['skip']} ({pct:.0f}%)")

        for slug, status in d["projects"]:
            marker = {"DONE": "+", "PENDING": " ", "SKIP": "-"}[status]
            print(f"    [{marker}] {slug}")

    grand_total = total_migrated + total_pending
    grand_pct = (total_migrated / max(grand_total, 1)) * 100

    print(f"\n  {'=' * 40}")
    print(f"  Total: {total_migrated}/{grand_total} migrated ({grand_pct:.0f}%), {total_skip} skipped")
    print(f"{'=' * 60}\n")


def verify_all():
    """Verify all migrated projects"""
    inventory = load_inventory()

    print(f"\n{'=' * 60}")
    print("  Verifying all migrated projects")
    print(f"{'=' * 60}\n")

    ok_count = 0
    fail_count = 0

    for proj in inventory["projects"]:
        if not proj.get("migrated", False):
            continue

        result = verify_single(proj)
        if result:
            ok_count += 1
        else:
            fail_count += 1

    print(f"\n  Verified: {ok_count} OK, {fail_count} issues")
    print(f"{'=' * 60}\n")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Safe incremental project migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project saas-crew             Migrate single project
  %(prog)s --domain 01_ABADA               Migrate all in domain
  %(prog)s --domain 01_ABADA --dry-run     Simulate without changes
  %(prog)s --status                        Show migration progress
  %(prog)s --verify                        Re-verify all migrated
  %(prog)s --rollback saas-crew            Undo migration
  %(prog)s --audit                         Git status check for all
  %(prog)s --scan-paths                    Find hardcoded paths
  %(prog)s --cleanup-symlinks              Remove all root symlinks
  %(prog)s --rename-domains                Rename domain dirs (01_ABADA etc)
  %(prog)s --rename-domains --dry-run      Simulate domain rename
  %(prog)s --move-all --force-move         Move all remaining (incl DIRTY)
  %(prog)s --move-all --force-move --dry-run  Simulate force move all
        """
    )
    parser.add_argument("--project", help="Migrate single project by slug")
    parser.add_argument("--domain", help="Migrate all projects in a domain")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--verify", action="store_true", help="Verify all migrated projects")
    parser.add_argument("--rollback", help="Rollback a migrated project by slug")
    parser.add_argument("--audit", action="store_true", help="Run git status audit on all projects")
    parser.add_argument("--scan-paths", action="store_true", help="Scan for hardcoded absolute paths")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without actual changes")
    parser.add_argument("--cleanup-symlinks", action="store_true", help="Remove all symlinks in ~/01_DEV root")
    parser.add_argument("--rename-domains", action="store_true", help="Rename domain dirs to numbered format")
    parser.add_argument("--move-all", action="store_true", help="Move all remaining unmigrated projects")
    parser.add_argument("--force-move", action="store_true", help="Force move even if git is dirty")

    args = parser.parse_args()

    # Validate INVENTORY.json exists
    if not INVENTORY_PATH.exists():
        print(f"Error: INVENTORY.json not found at {INVENTORY_PATH}")
        sys.exit(1)

    if args.cleanup_symlinks:
        cleanup_symlinks()
    elif args.rename_domains:
        rename_domains(dry_run=args.dry_run)
    elif args.move_all:
        move_all_remaining(force=args.force_move, dry_run=args.dry_run)
    elif args.status:
        show_status()
    elif args.verify:
        verify_all()
    elif args.audit:
        audit_all_projects()
    elif args.scan_paths:
        scan_hardcoded_paths()
    elif args.rollback:
        rollback_project(args.rollback)
    elif args.project:
        migrate_project(args.project, dry_run=args.dry_run, force=args.force_move)
    elif args.domain:
        migrate_domain(args.domain, dry_run=args.dry_run, force=args.force_move)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
