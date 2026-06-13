#!/usr/bin/env python3
"""
Statistics Page Generator
Generates development progress statistics page with charts
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict


def load_project_config(project_root: Path) -> Dict:
    """Load project configuration from project.json"""
    config_file = project_root / 'docs' / 'html' / 'data' / 'project.json'
    defaults = {'name': 'Project', 'description': 'Development Log', 'url': ''}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return {**defaults, **config}
        except Exception:
            pass
    return defaults


def generate_stats_html(data: dict) -> str:
    """Generate statistics HTML page"""
    stats = data['statistics']
    logs = data['logs']

    # Load project config
    project_root = Path(__file__).parent.parent
    config = load_project_config(project_root)
    project_name = config['name']
    project_desc = config['description']
    project_url = config.get('url', '')

    # Prepare data for charts
    categories = stats['categories']
    by_type = stats['by_type']

    # Calculate percentages for categories
    total_cat = sum(categories.values())
    cat_percentages = {k: round(v / total_cat * 100, 1) if total_cat > 0 else 0 for k, v in categories.items()}

    categories_json = json.dumps(categories)
    by_type_json = json.dumps(by_type)

    # Commits over time data
    commits_by_date = {}
    for log in logs:
        date_str = log.get('date', '')
        date_only = date_str.split(' ')[0] if ' ' in date_str else date_str
        if date_only:
            commits_by_date[date_only] = commits_by_date.get(date_only, 0) + 1
    commits_timeline_json = json.dumps(dict(sorted(commits_by_date.items())))

    footer_url = f'<p><a href="{project_url}" target="_blank">{project_url}</a></p>' if project_url else ''

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Development Statistics - {project_name}</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="scripts.js"></script>
</head>
<body>
    <!-- Dark Mode Toggle -->
    <button class="dark-mode-toggle" onclick="toggleDarkMode()" aria-label="Toggle Dark Mode">
        <span id="darkModeIcon">🌙</span>
        <span class="toggle-label" id="darkModeLabel">Dark</span>
    </button>

    <header class="page-header">
        <div class="header-content">
            <h1>Development Statistics</h1>
            <p class="header-subtitle">{project_desc}</p>
        </div>
        <nav class="stats-nav">
            <a href="index.html" class="nav-link">Kanban Board</a>
            <a href="timeline.html" class="nav-link">Timeline</a>
            <a href="heatmap.html" class="nav-link">Heatmap</a>
            <a href="files.html" class="nav-link">Files</a>
            <a href="commit-size.html" class="nav-link">Commit Size</a>
            <a href="time-analysis.html" class="nav-link">Time Analysis</a>
            <a href="deployment.html" class="nav-link">Deployment</a>
            <a href="stats.html" class="nav-link active">Statistics</a>
        </nav>
    </header>

    <main class="stats-container">
        <!-- Overall Stats -->
        <section class="stats-overview">
            <div class="stat-card">
                <div class="stat-card-header">Total Commits</div>
                <div class="stat-card-value">{stats['total_logs']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">Files Changed</div>
                <div class="stat-card-value">{stats['total_files_changed']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">Lines Added</div>
                <div class="stat-card-value text-green">+{stats['total_lines_added']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">Lines Deleted</div>
                <div class="stat-card-value text-red">-{stats['total_lines_deleted']:,}</div>
            </div>
        </section>

        <!-- Charts Grid -->
        <section class="charts-grid">
            <!-- Category Distribution -->
            <div class="chart-card">
                <h3 class="chart-title">Code Distribution</h3>
                <p class="chart-subtitle">Frontend / Backend / Docs / Config</p>
                <canvas id="categoryChart"></canvas>
                <div class="chart-legend">
                    <div class="legend-item">
                        <span class="legend-dot" style="background: #10b981;"></span>
                        <span>Frontend: {cat_percentages['frontend']}%</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-dot" style="background: #3b82f6;"></span>
                        <span>Backend: {cat_percentages['backend']}%</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-dot" style="background: #f59e0b;"></span>
                        <span>Docs: {cat_percentages['docs']}%</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-dot" style="background: #8b5cf6;"></span>
                        <span>Config: {cat_percentages['config']}%</span>
                    </div>
                </div>
            </div>

            <!-- Commit Type Distribution -->
            <div class="chart-card">
                <h3 class="chart-title">Commit Types</h3>
                <p class="chart-subtitle">Commit distribution by type</p>
                <canvas id="typeChart"></canvas>
            </div>

            <!-- Commits Over Time -->
            <div class="chart-card full-width">
                <h3 class="chart-title">Commits Over Time</h3>
                <p class="chart-subtitle">Daily commit activity</p>
                <canvas id="timelineChart"></canvas>
            </div>
        </section>
    </main>

    <footer class="page-footer">
        <p>Generated at {data['generated_at']} | {project_name}</p>
        {footer_url}
    </footer>

    <script>
        const categories = {categories_json};
        const byType = {by_type_json};
        const commitsTimeline = {commits_timeline_json};

        // Category Doughnut Chart
        new Chart(document.getElementById('categoryChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Frontend', 'Backend', 'Docs', 'Config'],
                datasets: [{{
                    data: [categories.frontend, categories.backend, categories.docs, categories.config],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});

        // Type Bar Chart
        new Chart(document.getElementById('typeChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(byType),
                datasets: [{{
                    label: 'Commits',
                    data: Object.values(byType),
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});

        // Commits Over Time Line Chart
        new Chart(document.getElementById('timelineChart'), {{
            type: 'line',
            data: {{
                labels: Object.keys(commitsTimeline),
                datasets: [{{
                    label: 'Commits',
                    data: Object.values(commitsTimeline),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    return html


def main():
    """Main function"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / 'docs' / 'html' / 'data' / 'dev-logs.json'
    output_file = project_root / 'docs' / 'html' / 'stats.html'

    # Load data
    print("\n[Loading] dev-logs data...")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[OK] Loaded {data['statistics']['total_logs']} logs")

    # Generate HTML
    print("\n[Generating] Statistics page...")
    html = generate_stats_html(data)

    # Save HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[SUCCESS] Statistics page generated!")
    print(f"[Output] {output_file}")
    print(f"\n[Browser] Open in browser:")
    print(f"   file://{output_file}")


if __name__ == '__main__':
    main()
