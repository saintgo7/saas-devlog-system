# Graph Report - .  (2026-06-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 363 nodes · 607 edges · 34 communities (24 shown, 10 thin omitted)
- Extraction: 99% EXTRACTED · 0% INFERRED · 1% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ac7b79fe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Project & DB Operations|Project & DB Operations]]
- [[_COMMUNITY_Project UI Interactions|Project UI Interactions]]
- [[_COMMUNITY_Dev Log System|Dev Log System]]
- [[_COMMUNITY_Heatmap Generation|Heatmap Generation]]
- [[_COMMUNITY_Deployment History|Deployment History]]
- [[_COMMUNITY_Project Auto-Registration|Project Auto-Registration]]
- [[_COMMUNITY_Timeline Generation|Timeline Generation]]
- [[_COMMUNITY_Deploy Script|Deploy Script]]
- [[_COMMUNITY_Rollback Script|Rollback Script]]
- [[_COMMUNITY_Kanban Board|Kanban Board]]
- [[_COMMUNITY_Time Analysis|Time Analysis]]
- [[_COMMUNITY_Sync to Database|Sync to Database]]
- [[_COMMUNITY_Dashboard UI|Dashboard UI]]
- [[_COMMUNITY_Commit Size Analysis|Commit Size Analysis]]
- [[_COMMUNITY_File Changes History|File Changes History]]
- [[_COMMUNITY_Devlog Parsing|Devlog Parsing]]
- [[_COMMUNITY_Search Functionality|Search Functionality]]
- [[_COMMUNITY_Devlog Commit Parsing|Devlog Commit Parsing]]
- [[_COMMUNITY_Dev Log Reports|Dev Log Reports]]
- [[_COMMUNITY_Statistics Generation|Statistics Generation]]
- [[_COMMUNITY_Restore Script|Restore Script]]
- [[_COMMUNITY_Setup Script|Setup Script]]
- [[_COMMUNITY_Backup Script|Backup Script]]
- [[_COMMUNITY_Database Initialization|Database Initialization]]
- [[_COMMUNITY_Logs Script|Logs Script]]
- [[_COMMUNITY_Startup Script|Startup Script]]
- [[_COMMUNITY_Deploy Workspace|Deploy Workspace]]
- [[_COMMUNITY_Install Script|Install Script]]
- [[_COMMUNITY_Update HTML|Update HTML]]
- [[_COMMUNITY_Install Devlog|Install Devlog]]
- [[_COMMUNITY_Update Devlog|Update Devlog]]
- [[_COMMUNITY_Uninstall Script|Uninstall Script]]

## God Nodes (most connected - your core abstractions)
1. `_load_project_paths()` - 13 edges
2. `get_db()` - 13 edges
3. `main()` - 11 edges
4. `log_info()` - 10 edges
5. `main()` - 10 edges
6. `generate_html()` - 10 edges
7. `Dev Log System - 배포 가이드` - 10 edges
8. `Dev Log System` - 10 edges
9. `Dev Log System` - 10 edges
10. `log_info()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Dev Log System Project Detail Screenshot` --references--> `Dev Log Admin - Project Detail`  [AMBIGUOUS]
  project-detail.png → admin/static/project.html
- `Dev Log System Project Detail Screenshot` --references--> `Dev Log Admin - Project Detail`  [AMBIGUOUS]
  project-detail-v2.png → admin/static/project.html
- `Dev Log System Project Detail Wide Screenshot` --references--> `Dev Log Admin - Project Detail`  [AMBIGUOUS]
  project-detail-wide.png → admin/static/project.html
- `Dev Log System Dashboard Screenshot` --references--> `Dev Log Admin - Dashboard`  [AMBIGUOUS]
  dashboard-full.png → admin/static/index.html
- `STATUS — saas-devlog-system` --references--> `Development Log #001 - 프로젝트 분석 및 현황 파악 (기타)`  [EXTRACTED]
  STATUS.md → template/docs/dev-log/001-2026-05-10-1000-project-analysis.md

## Import Cycles
- 1-file cycle: `template/scripts/generate-deployment.py -> template/scripts/generate-deployment.py`
- 1-file cycle: `template/scripts/generate-heatmap.py -> template/scripts/generate-heatmap.py`

## Communities (34 total, 10 thin omitted)

### Community 0 - "Project & DB Operations"
Cohesion: 0.06
Nodes (59): delete_project(), _detect_cicd(), _detect_platforms(), _detect_preview_entry_points(), _extract_domains(), general_exception_handler(), get_activity_heatmap(), get_commit_detail() (+51 more)

### Community 1 - "Project UI Interactions"
Cohesion: 0.16
Nodes (20): loadMoreCommits(), loadProject(), openCommitModal(), openProjectFolder(), openProjectIDE(), openProjectTerminal(), PLATFORM_STYLES, reloadCommits() (+12 more)

### Community 2 - "Dev Log System"
Cohesion: 0.23
Nodes (22): Dev Log Admin - SQLite Backend, Dev Log Admin Favicon, Dev Log Admin - Dashboard, Dev Log Admin - Project Detail, Dev Log Admin - Search, Dev Log System - CLAUDE.md Template, Dev Log Skill, Dev Log System Dashboard Screenshot (+14 more)

### Community 3 - "Heatmap Generation"
Cohesion: 0.18
Nodes (18): calculate_streak(), count_commits_by_date(), generate_heatmap_grid(), generate_html(), generate_legend_html(), get_date_only(), get_date_range(), load_project_config() (+10 more)

### Community 4 - "Deployment History"
Cohesion: 0.20
Nodes (16): analyze_deployment_frequency(), categorize_deployment(), format_date(), generate_html(), get_deployment_logs(), load_project_config(), main(), parse_date() (+8 more)

### Community 5 - "Project Auto-Registration"
Cohesion: 0.20
Nodes (14): detect_git_remote(), detect_tech_stack(), load_config(), main(), name_from_dirname(), Get git remote URL if available., Load existing config.json., Scan ~/01_DEV for project directories. (+6 more)

### Community 6 - "Timeline Generation"
Cohesion: 0.23
Nodes (14): format_date(), generate_html(), generate_timeline_item_html(), get_date_only(), get_type_info(), get_weekday(), group_logs_by_date(), load_project_config() (+6 more)

### Community 7 - "Deploy Script"
Cohesion: 0.43
Nodes (13): backup_current_state(), check_services(), cleanup(), health_check(), log_error(), log_info(), log_success(), log_warning() (+5 more)

### Community 8 - "Rollback Script"
Cohesion: 0.44
Nodes (12): check_previous_version(), health_check(), log_error(), log_info(), log_success(), log_warning(), main(), redeploy_services() (+4 more)

### Community 9 - "Kanban Board"
Cohesion: 0.27
Nodes (12): format_date(), generate_card_html(), generate_column_html(), generate_html(), get_type_info(), load_project_config(), main(), Generate HTML for a kanban column (+4 more)

### Community 10 - "Time Analysis"
Cohesion: 0.24
Nodes (12): analyze_by_hour(), analyze_by_weekday(), find_most_productive_time(), generate_html(), load_project_config(), main(), Load project configuration from project.json, Analyze commits by hour of day (+4 more)

### Community 11 - "Sync to Database"
Cohesion: 0.23
Nodes (11): Trigger sync from config.json, trigger_sync(), load_config(), main(), parse_full_content(), Sync single project to database, Parse full_content markdown to extract title, type, date, author, commit hash, a, Run sync and return results. Can be called from server.py or standalone. (+3 more)

### Community 12 - "Dashboard UI"
Cohesion: 0.26
Nodes (8): loadDashboard(), MINI_BADGE_STYLES, reloadData(), renderActivityHeatmap(), renderProjects(), renderRecentActivity(), renderTypeChart(), triggerSync()

### Community 13 - "Commit Size Analysis"
Cohesion: 0.29
Nodes (10): analyze_commit_sizes(), categorize_commit_size(), generate_html(), load_project_config(), main(), Load project configuration from project.json, Categorize commit by size, Analyze commit size distribution (+2 more)

### Community 14 - "File Changes History"
Cohesion: 0.29
Nodes (10): analyze_file_changes(), categorize_files(), generate_html(), load_project_config(), main(), Load project configuration from project.json, Analyze file changes across all commits, Categorize files by type (+2 more)

### Community 15 - "Devlog Parsing"
Cohesion: 0.29
Nodes (10): analyze_file_categories(), generate_statistics(), main(), parse_all_devlogs(), parse_devlog_file(), Parse all dev-log files in directory, Analyze file changes by category (frontend/backend/docs/etc), Parse a single dev-log markdown file (+2 more)

### Community 16 - "Search Functionality"
Cohesion: 0.35
Nodes (9): buildSearchUrl(), hideLoadMore(), loadMore(), performSearch(), readUrlParams(), renderResults(), updateLoadMore(), updateTypeFilterButtons() (+1 more)

### Community 18 - "Dev Log Reports"
Cohesion: 1.00
Nodes (8): Commit Size Analysis - Dev Log System, Deployment History - Dev Log System, File Changes History - Dev Log System, Activity Heatmap - Dev Log System, Dev Log System Development Progress, Development Statistics - Dev Log System, Time Analysis - Dev Log System, Development Timeline - Dev Log System

### Community 19 - "Statistics Generation"
Cohesion: 0.48
Nodes (6): generate_stats_html(), load_project_config(), main(), Load project configuration from project.json, Generate statistics HTML page, Path

### Community 20 - "Restore Script"
Cohesion: 0.60
Nodes (5): print_error(), print_info(), print_success(), print_warning(), restore.sh script

### Community 21 - "Setup Script"
Cohesion: 0.60
Nodes (5): print_error(), print_info(), print_success(), print_warning(), setup.sh script

### Community 22 - "Backup Script"
Cohesion: 0.70
Nodes (4): print_error(), print_info(), print_success(), backup.sh script

## Ambiguous Edges - Review These
- `Dev Log Admin - Dashboard` → `Dev Log System Dashboard Screenshot`  [AMBIGUOUS]
  dashboard-full.png · relation: references
- `Dev Log Admin - Project Detail` → `Dev Log System Project Detail Screenshot`  [AMBIGUOUS]
  project-detail.png · relation: references
- `Dev Log Admin - Project Detail` → `Dev Log System Project Detail Screenshot`  [AMBIGUOUS]
  project-detail-v2.png · relation: references
- `Dev Log Admin - Project Detail` → `Dev Log System Project Detail Wide Screenshot`  [AMBIGUOUS]
  project-detail-wide.png · relation: references

## Knowledge Gaps
- **18 isolated node(s):** `startup.sh script`, `MINI_BADGE_STYLES`, `TYPE_COLORS`, `PLATFORM_STYLES`, `WORKFLOW_TYPE_COLORS` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Dev Log Admin - Dashboard` and `Dev Log System Dashboard Screenshot`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Dev Log Admin - Project Detail` and `Dev Log System Project Detail Screenshot`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Dev Log Admin - Project Detail` and `Dev Log System Project Detail Screenshot`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Dev Log Admin - Project Detail` and `Dev Log System Project Detail Wide Screenshot`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `trigger_sync()` connect `Sync to Database` to `Project & DB Operations`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `generate_html()` connect `Timeline Generation` to `Kanban Board`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **What connects `Generate a URL-friendly slug from directory name.`, `Generate a human-readable name from directory name.`, `Detect tech stack from project files.` to the rest of the system?**
  _97 weakly-connected nodes found - possible documentation gaps or missing edges._