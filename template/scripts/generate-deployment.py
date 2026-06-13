#!/usr/bin/env python3
"""
Deployment History Generator for Dev Log
Generates deployment history and CI/CD analysis from parsed dev-logs JSON
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict


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


def get_deployment_logs(logs: List[Dict]) -> List[Dict]:
    """Get deployment-related logs (CI/CD commits)"""
    deployment_logs = []

    for log in logs:
        log_type = log.get('type', '')
        full_content = log.get('full_content', '').lower()
        title = log.get('title', '').lower()

        # Check if it's deployment related
        is_deployment = (
            log_type == 'ci' or
            'deploy' in title or
            'workflow' in title or
            'docker' in title or
            'ci/cd' in title or
            '.github/workflows' in full_content or
            'docker-compose' in full_content
        )

        if is_deployment:
            deployment_logs.append(log)

    return deployment_logs


def categorize_deployment(log: Dict) -> str:
    """Categorize deployment by type"""
    title = log.get('title', '').lower()
    full_content = log.get('full_content', '').lower()

    if 'fix' in title or 'bug' in title:
        return 'hotfix'
    elif 'workflow' in title or '.github/workflows' in full_content:
        return 'ci-config'
    elif 'docker' in title or 'docker-compose' in full_content:
        return 'infrastructure'
    else:
        return 'release'


def parse_date(date_str: str) -> datetime:
    """Parse date string with flexible format"""
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.now()


def analyze_deployment_frequency(logs: List[Dict]) -> Dict:
    """Analyze deployment frequency by time period"""
    if not logs:
        return {'daily': 0, 'weekly': 0, 'monthly': 0}

    # Sort by date
    sorted_logs = sorted(logs, key=lambda x: x.get('date', ''))

    if len(sorted_logs) < 2:
        return {'daily': 0, 'weekly': 0, 'monthly': 0}

    first_date = parse_date(sorted_logs[0]['date'])
    last_date = parse_date(sorted_logs[-1]['date'])

    total_days = (last_date - first_date).days + 1
    total_weeks = total_days / 7
    total_months = total_days / 30

    return {
        'daily': round(len(logs) / total_days, 2) if total_days > 0 else 0,
        'weekly': round(len(logs) / total_weeks, 2) if total_weeks > 0 else 0,
        'monthly': round(len(logs) / total_months, 2) if total_months > 0 else 0
    }


def format_date(date_str: str) -> str:
    """Format date string"""
    dt = parse_date(date_str)
    return dt.strftime('%Y-%m-%d %H:%M')


def generate_html(data: Dict) -> str:
    """Generate deployment history HTML page"""
    stats = data['statistics']
    logs = data['logs']
    generated_at = data.get('generated_at', '')

    # Load project config
    project_root = Path(__file__).parent.parent
    config = load_project_config(project_root)
    project_name = config['name']
    project_url = config.get('url', '')
    footer_url = f'<p><a href="{project_url}" target="_blank">{project_url}</a></p>' if project_url else ''

    # Get deployment logs
    deployment_logs = get_deployment_logs(logs)

    # Categorize deployments
    deployment_categories = defaultdict(list)
    for log in deployment_logs:
        category = categorize_deployment(log)
        deployment_categories[category].append(log)

    # Analyze frequency
    frequency = analyze_deployment_frequency(deployment_logs)

    # Prepare data for JavaScript
    deployment_logs_json = json.dumps(deployment_logs, ensure_ascii=False)
    categories_json = json.dumps({
        'hotfix': len(deployment_categories['hotfix']),
        'ci-config': len(deployment_categories['ci-config']),
        'infrastructure': len(deployment_categories['infrastructure']),
        'release': len(deployment_categories['release'])
    })

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deployment History - {project_name}</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
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
            <h1>🚀 Deployment History</h1>
            <p class="header-subtitle">배포 히스토리 및 CI/CD 분석</p>
        </div>
        <nav class="stats-nav">
            <a href="index.html" class="nav-link">Kanban Board</a>
            <a href="timeline.html" class="nav-link">Timeline</a>
            <a href="heatmap.html" class="nav-link">Heatmap</a>
            <a href="files.html" class="nav-link">Files</a>
            <a href="commit-size.html" class="nav-link">Commit Size</a>
            <a href="time-analysis.html" class="nav-link">Time Analysis</a>
            <a href="deployment.html" class="nav-link active">Deployment</a>
            <a href="stats.html" class="nav-link">Statistics</a>
        </nav>
    </header>

    <main class="deployment-container">
        <!-- Summary Cards -->
        <section class="deployment-summary">
            <div class="summary-card">
                <div class="summary-value">{len(deployment_logs)}</div>
                <div class="summary-label">Total Deployments</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{frequency['weekly']}</div>
                <div class="summary-label">Per Week (Avg)</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{len(deployment_categories['hotfix'])}</div>
                <div class="summary-label">Hotfixes</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{len(deployment_categories['infrastructure'])}</div>
                <div class="summary-label">Infrastructure</div>
            </div>
        </section>

        <!-- Deployment Info -->
        <section class="deployment-info">
            <div class="info-card">
                <h3>🌐 Production Environment</h3>
                <div class="info-content">
                    <div class="info-item">
                        <span class="info-label">URL:</span>
                        {'<a href="' + project_url + '" target="_blank">' + project_url + '</a>' if project_url else '<span>Not configured</span>'}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Trigger:</span>
                        <span>Push to main branch</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Workflow:</span>
                        <span>GitHub Actions CD</span>
                    </div>
                </div>
            </div>

            <div class="info-card">
                <h3>📦 Deployment Process</h3>
                <div class="deployment-steps">
                    <div class="step">
                        <span class="step-number">1</span>
                        <span class="step-text">Update code from main</span>
                    </div>
                    <div class="step">
                        <span class="step-number">2</span>
                        <span class="step-text">Rebuild containers</span>
                    </div>
                    <div class="step">
                        <span class="step-number">3</span>
                        <span class="step-text">Health check (30s)</span>
                    </div>
                    <div class="step">
                        <span class="step-number">4</span>
                        <span class="step-text">Verify status</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- Charts Grid -->
        <section class="charts-grid">
            <!-- Deployment Category Distribution -->
            <div class="chart-card">
                <h3 class="chart-title">Deployment Types</h3>
                <p class="chart-subtitle">배포 타입별 분포</p>
                <canvas id="categoryChart"></canvas>
            </div>

            <!-- Deployment Frequency -->
            <div class="chart-card">
                <h3 class="chart-title">Deployment Frequency</h3>
                <p class="chart-subtitle">배포 빈도</p>
                <div class="frequency-stats">
                    <div class="freq-item">
                        <div class="freq-value">{frequency['daily']}</div>
                        <div class="freq-label">Per Day</div>
                    </div>
                    <div class="freq-item">
                        <div class="freq-value">{frequency['weekly']}</div>
                        <div class="freq-label">Per Week</div>
                    </div>
                    <div class="freq-item">
                        <div class="freq-value">{frequency['monthly']}</div>
                        <div class="freq-label">Per Month</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Deployment Timeline -->
        <section class="deployment-timeline">
            <h2 class="section-title">Deployment Timeline</h2>
            <div class="timeline-list">
    '''

    # Add deployment timeline items
    for log in sorted(deployment_logs, key=lambda x: x.get('date', ''), reverse=True):
        category = categorize_deployment(log)
        category_colors = {
            'hotfix': '#ef4444',
            'ci-config': '#06b6d4',
            'infrastructure': '#8b5cf6',
            'release': '#10b981'
        }
        color = category_colors.get(category, '#6b7280')

        title = log.get('title', 'Untitled')
        date = format_date(log.get('date', ''))
        commit = log.get('commit', 'N/A')[:7]
        log_number = log.get('log_number', '?')

        html += f'''
                <div class="timeline-deploy-item" style="border-left-color: {color}">
                    <div class="deploy-header">
                        <span class="deploy-badge" style="background-color: {color}">{category.upper()}</span>
                        <span class="deploy-number">#{log_number}</span>
                        <span class="deploy-date">{date}</span>
                    </div>
                    <h4 class="deploy-title">{title}</h4>
                    <div class="deploy-meta">
                        <span class="deploy-commit">Commit: {commit}</span>
                    </div>
                </div>
        '''

    html += f'''
            </div>
        </section>

        <!-- Deployment Best Practices -->
        <section class="best-practices">
            <h2 class="section-title">📋 Deployment Best Practices</h2>
            <div class="practices-grid">
                <div class="practice-card">
                    <h4>✅ Automated Testing</h4>
                    <p>모든 배포 전 자동화된 테스트 실행</p>
                </div>
                <div class="practice-card">
                    <h4>🔄 Continuous Integration</h4>
                    <p>main 브랜치에 머지 시 자동 배포</p>
                </div>
                <div class="practice-card">
                    <h4>🏥 Health Checks</h4>
                    <p>배포 후 서비스 헬스 체크 필수</p>
                </div>
                <div class="practice-card">
                    <h4>📝 Release Notes</h4>
                    <p>각 배포마다 변경사항 문서화</p>
                </div>
                <div class="practice-card">
                    <h4>🔙 Rollback Plan</h4>
                    <p>문제 발생 시 빠른 롤백 준비</p>
                </div>
                <div class="practice-card">
                    <h4>🔔 Monitoring</h4>
                    <p>배포 후 모니터링 및 알림 설정</p>
                </div>
            </div>
        </section>
    </main>

    <footer class="page-footer">
        <p>Generated at {generated_at} | {project_name}</p>
        {footer_url}
    </footer>

    <script>
        const categories = {categories_json};

        // Category Doughnut Chart
        new Chart(document.getElementById('categoryChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Hotfix', 'CI Config', 'Infrastructure', 'Release'],
                datasets: [{{
                    data: [
                        categories.hotfix,
                        categories['ci-config'],
                        categories.infrastructure,
                        categories.release
                    ],
                    backgroundColor: ['#ef4444', '#06b6d4', '#8b5cf6', '#10b981'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
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
    output_file = project_root / 'docs' / 'html' / 'deployment.html'

    # Load data
    print("\n[Loading] dev-logs data...")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[OK] Loaded {data['statistics']['total_logs']} logs")

    # Generate HTML
    print("\n[Generating] Deployment History HTML...")
    html = generate_html(data)

    # Save HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[SUCCESS] Deployment History HTML generated successfully!")
    print(f"[Output] {output_file}")
    print(f"\n[Browser] Open in browser:")
    print(f"   file://{output_file}")


if __name__ == '__main__':
    main()
