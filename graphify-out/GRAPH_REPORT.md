# Graph Report - .  (2026-06-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 416 nodes · 613 edges · 44 communities (34 shown, 10 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4930194f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Inventory & System Maintenance|Inventory & System Maintenance]]
- [[_COMMUNITY_Server & Project Monitoring|Server & Project Monitoring]]
- [[_COMMUNITY_Kanban HTML Generation|Kanban HTML Generation]]
- [[_COMMUNITY_Database Sync & Migration|Database Sync & Migration]]
- [[_COMMUNITY_Commit Heatmap Generation|Commit Heatmap Generation]]
- [[_COMMUNITY_Commit Heatmap Generation|Commit Heatmap Generation]]
- [[_COMMUNITY_System Inventory Scanning|System Inventory Scanning]]
- [[_COMMUNITY_Deployment Operations|Deployment Operations]]
- [[_COMMUNITY_Deployment Log Analysis|Deployment Log Analysis]]
- [[_COMMUNITY_Deployment Log Analysis|Deployment Log Analysis]]
- [[_COMMUNITY_Dev Log System Overview|Dev Log System Overview]]
- [[_COMMUNITY_Rollback Operations|Rollback Operations]]
- [[_COMMUNITY_Timeline HTML Generation|Timeline HTML Generation]]
- [[_COMMUNITY_Dev Log Parsing & Stats|Dev Log Parsing & Stats]]
- [[_COMMUNITY_Dev Log Parsing & Stats|Dev Log Parsing & Stats]]
- [[_COMMUNITY_Time Usage Analysis|Time Usage Analysis]]
- [[_COMMUNITY_Kanban HTML Generation|Kanban HTML Generation]]
- [[_COMMUNITY_Time Usage Analysis|Time Usage Analysis]]
- [[_COMMUNITY_Activity Visualization|Activity Visualization]]
- [[_COMMUNITY_Dev Log Script|Dev Log Script]]
- [[_COMMUNITY_Dev Log Script|Dev Log Script]]
- [[_COMMUNITY_Commit Size Analysis|Commit Size Analysis]]
- [[_COMMUNITY_File Changes Analysis|File Changes Analysis]]
- [[_COMMUNITY_Commit Size Analysis|Commit Size Analysis]]
- [[_COMMUNITY_File Changes Analysis|File Changes Analysis]]
- [[_COMMUNITY_Dashboard Rendering|Dashboard Rendering]]
- [[_COMMUNITY_Restore Script|Restore Script]]
- [[_COMMUNITY_Setup Script|Setup Script]]
- [[_COMMUNITY_Backup Script|Backup Script]]
- [[_COMMUNITY_Dashboard Features|Dashboard Features]]
- [[_COMMUNITY_Statistics Generation|Statistics Generation]]
- [[_COMMUNITY_Statistics Generation|Statistics Generation]]
- [[_COMMUNITY_Dev Log System|Dev Log System]]
- [[_COMMUNITY_Logs Script|Logs Script]]
- [[_COMMUNITY_Install Script|Install Script]]
- [[_COMMUNITY_Deploy Script|Deploy Script]]
- [[_COMMUNITY_Update HTML Script|Update HTML Script]]
- [[_COMMUNITY_Install Devlog Script|Install Devlog Script]]
- [[_COMMUNITY_Update HTML Script|Update HTML Script]]
- [[_COMMUNITY_Update Devlog Script|Update Devlog Script]]
- [[_COMMUNITY_Uninstall Script|Uninstall Script]]

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 16 edges
2. `main()` - 11 edges
3. `main()` - 11 edges
4. `load_inventory()` - 10 edges
5. `log_info()` - 10 edges
6. `main()` - 10 edges
7. `migrate_single()` - 9 edges
8. `log_info()` - 9 edges
9. `log()` - 8 edges
10. `pre_check()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Dev Log System` --references--> `Dev Log System`  [EXTRACTED]
  DISTRIBUTION.md → README.md
- `Dev Log System` --references--> `Dev Log System`  [EXTRACTED]
  README.ko.md → README.md
- `Initial Release` --cites--> `Dev Log System`  [EXTRACTED]
  docs/dev-log/01-2026-02-05-1920-initial-release.md → README.md
- `Dev Log System` --references--> `Dev Log Admin`  [EXTRACTED]
  README.md → admin/README.md
- `Dev Log System` --references--> `Dev Log`  [EXTRACTED]
  README.md → docs/ARCHITECTURE.md

## Import Cycles
- 1-file cycle: `scripts/generate-deployment.py -> scripts/generate-deployment.py`
- 1-file cycle: `scripts/generate-heatmap.py -> scripts/generate-heatmap.py`
- 1-file cycle: `template/scripts/generate-deployment.py -> template/scripts/generate-deployment.py`
- 1-file cycle: `template/scripts/generate-heatmap.py -> template/scripts/generate-heatmap.py`

## Communities (44 total, 10 thin omitted)

### Community 0 - "Inventory & System Maintenance"
Cohesion: 0.11
Nodes (42): audit_all_projects(), check_docker_running(), check_git_status(), cleanup_symlinks(), get_dirty_files(), load_config(), load_inventory(), log() (+34 more)

### Community 1 - "Server & Project Monitoring"
Cohesion: 0.10
Nodes (28): get_commit_detail(), get_db(), get_infrastructure_stats(), get_overview_stats(), get_project(), get_project_commits(), get_project_deployments(), get_server() (+20 more)

### Community 2 - "Kanban HTML Generation"
Cohesion: 0.15
Nodes (20): format_date(), generate_card_html(), generate_column_html(), generate_html(), get_type_info(), main(), Generate HTML for a kanban column, Generate complete HTML page (+12 more)

### Community 3 - "Database Sync & Migration"
Cohesion: 0.17
Nodes (14): init_db(), migrate_db(), Initialize SQLite database with schema, Add new columns to existing tables (safe migration), load_config(), main(), Sync deployment mappings for a project, Sync Cloudflare tunnel data (+6 more)

### Community 4 - "Commit Heatmap Generation"
Cohesion: 0.21
Nodes (15): datetime, calculate_streak(), count_commits_by_date(), generate_heatmap_grid(), generate_html(), generate_legend_html(), get_date_only(), get_date_range() (+7 more)

### Community 5 - "Commit Heatmap Generation"
Cohesion: 0.21
Nodes (15): datetime, calculate_streak(), count_commits_by_date(), generate_heatmap_grid(), generate_html(), generate_legend_html(), get_date_only(), get_date_range() (+7 more)

### Community 6 - "System Inventory Scanning"
Cohesion: 0.21
Nodes (13): main(), parse_cloudflare_yml(), Simple YAML parser for cloudflare config (no dependency), Scan directory for git projects, Scan a single project directory, Merge scan results into config.json, Parse ~/.ssh/config for server entries, Parse ~/.cloudflared/config.yml for tunnel entries (+5 more)

### Community 7 - "Deployment Operations"
Cohesion: 0.43
Nodes (13): backup_current_state(), check_services(), cleanup(), health_check(), log_error(), log_info(), log_success(), log_warning() (+5 more)

### Community 8 - "Deployment Log Analysis"
Cohesion: 0.23
Nodes (13): datetime, analyze_deployment_frequency(), categorize_deployment(), format_date(), generate_html(), get_deployment_logs(), main(), parse_date() (+5 more)

### Community 9 - "Deployment Log Analysis"
Cohesion: 0.23
Nodes (13): datetime, analyze_deployment_frequency(), categorize_deployment(), format_date(), generate_html(), get_deployment_logs(), main(), parse_date() (+5 more)

### Community 10 - "Dev Log System Overview"
Cohesion: 0.18
Nodes (13): Dev Log Admin, Dev Log Admin, Dev Log System, Dev Log, Initial Release, Implement Admin Dashboard, Dev Log System, Dev Log System (+5 more)

### Community 11 - "Rollback Operations"
Cohesion: 0.44
Nodes (12): check_previous_version(), health_check(), log_error(), log_info(), log_success(), log_warning(), main(), redeploy_services() (+4 more)

### Community 12 - "Timeline HTML Generation"
Cohesion: 0.24
Nodes (12): format_date(), generate_html(), generate_timeline_item_html(), get_date_only(), get_type_info(), get_weekday(), group_logs_by_date(), main() (+4 more)

### Community 13 - "Dev Log Parsing & Stats"
Cohesion: 0.29
Nodes (10): Path, analyze_file_categories(), generate_statistics(), main(), parse_all_devlogs(), parse_devlog_file(), Parse all dev-log files in directory, Analyze file changes by category (frontend/backend/docs/etc) (+2 more)

### Community 14 - "Dev Log Parsing & Stats"
Cohesion: 0.29
Nodes (10): Path, analyze_file_categories(), generate_statistics(), main(), parse_all_devlogs(), parse_devlog_file(), Parse all dev-log files in directory, Analyze file changes by category (frontend/backend/docs/etc) (+2 more)

### Community 15 - "Time Usage Analysis"
Cohesion: 0.29
Nodes (9): analyze_by_hour(), analyze_by_weekday(), find_most_productive_time(), generate_html(), main(), Analyze commits by hour of day, Analyze commits by day of week, Find most productive time period (+1 more)

### Community 16 - "Kanban HTML Generation"
Cohesion: 0.33
Nodes (9): format_date(), generate_card_html(), generate_column_html(), generate_html(), get_type_info(), main(), Generate HTML for a kanban column, Generate complete HTML page (+1 more)

### Community 17 - "Time Usage Analysis"
Cohesion: 0.29
Nodes (9): analyze_by_hour(), analyze_by_weekday(), find_most_productive_time(), generate_html(), main(), Analyze commits by hour of day, Analyze commits by day of week, Find most productive time period (+1 more)

### Community 18 - "Activity Visualization"
Cohesion: 0.22
Nodes (9): Commit Size Analysis, Deployment History, File Changes History, Activity Heatmap, Kanban Board, Dev Log, Statistics, Time Analysis (+1 more)

### Community 21 - "Commit Size Analysis"
Cohesion: 0.36
Nodes (7): analyze_commit_sizes(), categorize_commit_size(), generate_html(), main(), Categorize commit by size, Analyze commit size distribution, Generate commit size analysis HTML page

### Community 22 - "File Changes Analysis"
Cohesion: 0.36
Nodes (7): analyze_file_changes(), categorize_files(), generate_html(), main(), Analyze file changes across all commits, Categorize files by type, Generate files history HTML page

### Community 23 - "Commit Size Analysis"
Cohesion: 0.36
Nodes (7): analyze_commit_sizes(), categorize_commit_size(), generate_html(), main(), Categorize commit by size, Analyze commit size distribution, Generate commit size analysis HTML page

### Community 24 - "File Changes Analysis"
Cohesion: 0.36
Nodes (7): analyze_file_changes(), categorize_files(), generate_html(), main(), Analyze file changes across all commits, Categorize files by type, Generate files history HTML page

### Community 25 - "Dashboard Rendering"
Cohesion: 0.43
Nodes (4): loadDashboard(), renderProjects(), renderRecentActivity(), renderTypeChart()

### Community 26 - "Restore Script"
Cohesion: 0.60
Nodes (5): print_error(), print_info(), print_success(), print_warning(), restore.sh script

### Community 27 - "Setup Script"
Cohesion: 0.60
Nodes (5): print_error(), print_info(), print_success(), print_warning(), setup.sh script

### Community 29 - "Backup Script"
Cohesion: 0.70
Nodes (4): print_error(), print_info(), print_success(), backup.sh script

### Community 31 - "Dashboard Features"
Cohesion: 0.50
Nodes (4): Deployments, Dashboard, Infrastructure, Search

### Community 32 - "Statistics Generation"
Cohesion: 0.67
Nodes (3): generate_stats_html(), main(), Generate statistics HTML page

### Community 33 - "Statistics Generation"
Cohesion: 0.67
Nodes (3): generate_stats_html(), main(), Generate statistics HTML page

### Community 34 - "Dev Log System"
Cohesion: 0.67
Nodes (3): Dev Log System, Dev Log Skill, Dev Log System

## Knowledge Gaps
- **27 isolated node(s):** `install.sh script`, `dev-log.sh script`, `update-html.sh script`, `install-devlog.sh script`, `deploy-ws.sh script` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Initialize SQLite database with schema`, `Add new columns to existing tables (safe migration)`, `Check git status for a project directory.     Returns: 'CLEAN', 'DIRTY', or 'NO-` to the rest of the system?**
  _134 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Inventory & System Maintenance` be split into smaller, more focused modules?**
  _Cohesion score 0.10631229235880399 - nodes in this community are weakly interconnected._
- **Should `Server & Project Monitoring` be split into smaller, more focused modules?**
  _Cohesion score 0.10344827586206896 - nodes in this community are weakly interconnected._
- **Should `Kanban HTML Generation` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._