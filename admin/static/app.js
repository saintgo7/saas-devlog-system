// Dev Log Admin - Main JavaScript
const API_BASE = '';

// Dashboard page
async function loadDashboard() {
    try {
        const [projectsRes, statsRes, heatmapRes, badgesRes, previewBadgesRes] = await Promise.all([
            fetch(`${API_BASE}/api/projects`),
            fetch(`${API_BASE}/api/stats/overview`),
            fetch(`${API_BASE}/api/stats/activity-heatmap?days=90`),
            fetch(`${API_BASE}/api/projects/deployment-badges`),
            fetch(`${API_BASE}/api/projects/preview-badges`)
        ]);

        const projects = await projectsRes.json();
        const stats = await statsRes.json();
        const heatmapData = await heatmapRes.json();
        const badges = badgesRes.ok ? await badgesRes.json() : {};
        const previewBadges = previewBadgesRes.ok ? await previewBadgesRes.json() : {};

        // Update stats
        document.getElementById('totalProjects').textContent = stats.total_projects;
        document.getElementById('totalCommits').textContent = stats.total_commits.toLocaleString();
        document.getElementById('recentActivity').textContent =
            stats.recent_activity[0]?.date.substring(0, 10) || 'N/A';

        // Render charts and lists
        renderTypeChart(stats.commits_by_type);
        renderActivityHeatmap(heatmapData);
        renderProjects(projects, badges, previewBadges);
        renderRecentActivity(stats.recent_activity);

    } catch (error) {
        console.error('Failed to load dashboard:', error);
        alert('데이터 로딩 실패: ' + error.message);
    }
}

function renderTypeChart(typeStats) {
    const typeColors = {
        'feat': '#10b981', 'fix': '#ef4444', 'refactor': '#8b5cf6',
        'docs': '#3b82f6', 'test': '#f59e0b', 'chore': '#6b7280',
        'ci': '#06b6d4', 'perf': '#ec4899'
    };

    const chart = document.getElementById('typeChart');
    const total = Object.values(typeStats).reduce((a, b) => a + b, 0);

    chart.textContent = '';
    Object.entries(typeStats)
        .sort((a, b) => b[1] - a[1])
        .forEach(([type, count]) => {
            const percentage = (count / total * 100).toFixed(1);

            const barDiv = document.createElement('div');
            barDiv.className = 'type-bar';

            const labelDiv = document.createElement('div');
            labelDiv.className = 'type-label';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'type-name';
            nameSpan.textContent = type;

            const countSpan = document.createElement('span');
            countSpan.className = 'type-count';
            countSpan.textContent = `${count} (${percentage}%)`;

            labelDiv.appendChild(nameSpan);
            labelDiv.appendChild(countSpan);

            const progressDiv = document.createElement('div');
            progressDiv.className = 'type-progress';

            const fillDiv = document.createElement('div');
            fillDiv.className = 'type-fill';
            fillDiv.style.width = `${percentage}%`;
            fillDiv.style.backgroundColor = typeColors[type] || '#6b7280';

            progressDiv.appendChild(fillDiv);
            barDiv.appendChild(labelDiv);
            barDiv.appendChild(progressDiv);
            chart.appendChild(barDiv);
        });
}

function renderActivityHeatmap(data) {
    const container = document.getElementById('activityHeatmap');
    container.textContent = '';

    // Build a date->count map from API data
    const countMap = {};
    data.forEach(d => { countMap[d.date] = d.count; });

    // Determine date range: last 90 days ending today
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const startDate = new Date(today);
    startDate.setDate(startDate.getDate() - 89);

    // Align start to the previous Monday
    const startDay = startDate.getDay(); // 0=Sun
    const mondayOffset = startDay === 0 ? -6 : 1 - startDay;
    startDate.setDate(startDate.getDate() + mondayOffset);

    // Color scale
    function getColor(count) {
        if (count === 0) return '#ebedf0';
        if (count <= 2) return '#c6d4f7';
        if (count <= 5) return '#8fa5eb';
        return '#667eea';
    }

    // Build grid
    const grid = document.createElement('div');
    grid.className = 'heatmap-grid';

    const dayLabels = ['Mon', '', 'Wed', '', 'Fri', '', ''];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Calculate total weeks
    const diffTime = today.getTime() - startDate.getTime();
    const totalDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1;
    const totalWeeks = Math.ceil(totalDays / 7);

    // First column: day-of-week labels (row 0 = month label placeholder, rows 1-7 = days)
    // Month label placeholder for label column
    const emptyMonth = document.createElement('div');
    emptyMonth.className = 'heatmap-month-label';
    grid.appendChild(emptyMonth);

    for (let row = 0; row < 7; row++) {
        const label = document.createElement('div');
        label.className = 'heatmap-label';
        label.textContent = dayLabels[row];
        grid.appendChild(label);
    }

    // Week columns
    let lastMonth = -1;
    for (let week = 0; week < totalWeeks; week++) {
        // Month label row
        const weekStart = new Date(startDate);
        weekStart.setDate(weekStart.getDate() + week * 7);
        const monthLabel = document.createElement('div');
        monthLabel.className = 'heatmap-month-label';
        if (weekStart.getMonth() !== lastMonth) {
            monthLabel.textContent = monthNames[weekStart.getMonth()];
            lastMonth = weekStart.getMonth();
        }
        grid.appendChild(monthLabel);

        // Day cells (Mon=0 through Sun=6)
        for (let day = 0; day < 7; day++) {
            const cellDate = new Date(startDate);
            cellDate.setDate(cellDate.getDate() + week * 7 + day);

            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';

            if (cellDate > today) {
                cell.style.backgroundColor = 'transparent';
            } else {
                const dateStr = cellDate.toISOString().slice(0, 10);
                const count = countMap[dateStr] || 0;
                cell.style.backgroundColor = getColor(count);
                cell.title = `${dateStr}: ${count} commit${count !== 1 ? 's' : ''}`;
            }

            grid.appendChild(cell);
        }
    }

    container.appendChild(grid);

    // Legend
    const legend = document.createElement('div');
    legend.className = 'heatmap-legend';
    legend.appendChild(document.createTextNode('Less'));
    ['#ebedf0', '#c6d4f7', '#8fa5eb', '#667eea'].forEach(color => {
        const box = document.createElement('div');
        box.className = 'heatmap-legend-cell';
        box.style.backgroundColor = color;
        legend.appendChild(box);
    });
    legend.appendChild(document.createTextNode('More'));
    container.appendChild(legend);
}

const MINI_BADGE_STYLES = {
    'Vercel': { bg: '#000000', color: '#ffffff' },
    'Cloudflare': { bg: '#f48120', color: '#ffffff' },
    'Docker': { bg: '#2496ed', color: '#ffffff' },
    'Netlify': { bg: '#00c7b7', color: '#ffffff' },
    'GitHub Pages': { bg: '#24292f', color: '#ffffff' },
    'Firebase': { bg: '#ffca28', color: '#1a1a1a' },
    'Fly.io': { bg: '#7b36ed', color: '#ffffff' },
    'Google Cloud': { bg: '#4285f4', color: '#ffffff' },
    'Render': { bg: '#46e3b7', color: '#1a1a1a' },
};

function renderProjects(projects, badges, previewBadges) {
    const grid = document.getElementById('projectsGrid');
    grid.textContent = '';

    projects.forEach(proj => {
        const card = document.createElement('div');
        card.className = 'project-card';

        const header = document.createElement('div');
        header.className = 'project-header';
        const h3 = document.createElement('h3');
        h3.textContent = proj.name;
        const commits = document.createElement('span');
        commits.className = 'project-commits';
        commits.textContent = `${proj.total_commits} commits`;
        header.appendChild(h3);
        header.appendChild(commits);

        // Thumbnail / Preview placeholder
        const pb = previewBadges && previewBadges[proj.slug];
        if (pb && pb.has_thumbnail) {
            const thumbDiv = document.createElement('div');
            thumbDiv.className = 'project-thumbnail';
            thumbDiv.onclick = () => {
                if (pb.primary_preview_url) {
                    window.open(pb.primary_preview_url, '_blank');
                }
            };
            const thumbImg = document.createElement('img');
            thumbImg.className = 'project-thumbnail-img';
            thumbImg.src = pb.thumbnail_url;
            thumbImg.alt = proj.name + ' preview';
            thumbImg.loading = 'lazy';
            thumbDiv.appendChild(thumbImg);
            card.appendChild(header);
            card.appendChild(thumbDiv);
        } else if (pb && pb.has_preview) {
            const thumbDiv = document.createElement('div');
            thumbDiv.className = 'project-thumbnail';
            thumbDiv.onclick = () => {
                if (pb.primary_preview_url) {
                    window.open(pb.primary_preview_url, '_blank');
                }
            };
            const placeholder = document.createElement('div');
            placeholder.className = 'project-thumbnail-placeholder';
            const typeText = pb.preview_types.join(' + ');
            placeholder.textContent = 'Preview: ' + typeText;
            thumbDiv.appendChild(placeholder);
            card.appendChild(header);
            card.appendChild(thumbDiv);
        } else {
            card.appendChild(header);
        }

        const desc = document.createElement('p');
        desc.className = 'project-desc';
        desc.textContent = proj.description || '';

        const techDiv = document.createElement('div');
        techDiv.className = 'project-tech';
        proj.tech_stack.forEach(tech => {
            const tag = document.createElement('span');
            tag.className = 'tech-tag';
            tag.textContent = tech;
            techDiv.appendChild(tag);
        });

        // Deployment badges
        const badgeData = badges && badges[proj.slug];
        let badgesDiv = null;
        if (badgeData && (badgeData.platforms.length > 0 || badgeData.has_ci)) {
            badgesDiv = document.createElement('div');
            badgesDiv.className = 'project-deploy-badges';
            badgeData.platforms.forEach(p => {
                const badge = document.createElement('span');
                badge.className = 'deploy-mini-badge';
                const style = MINI_BADGE_STYLES[p] || { bg: '#6b7280', color: '#ffffff' };
                badge.style.backgroundColor = style.bg;
                badge.style.color = style.color;
                badge.textContent = p;
                badgesDiv.appendChild(badge);
            });
            if (badgeData.has_ci) {
                const ciBadge = document.createElement('span');
                ciBadge.className = 'deploy-mini-badge';
                ciBadge.style.backgroundColor = '#10b981';
                ciBadge.style.color = '#ffffff';
                ciBadge.textContent = 'CI/CD';
                badgesDiv.appendChild(ciBadge);
            }
        }

        const actions = document.createElement('div');
        actions.className = 'project-actions';
        const viewLink = document.createElement('a');
        viewLink.href = `/project.html?slug=${proj.slug}`;
        viewLink.className = 'btn-primary';
        viewLink.textContent = 'View Details →';
        actions.appendChild(viewLink);

        const folderBtn = document.createElement('button');
        folderBtn.className = 'btn-folder';
        folderBtn.textContent = 'Open Folder';
        folderBtn.onclick = () => openProjectFolder(proj.slug);
        actions.appendChild(folderBtn);

        const termBtn = document.createElement('button');
        termBtn.className = 'btn-terminal';
        termBtn.textContent = 'Terminal';
        termBtn.onclick = () => openProjectTerminal(proj.slug);
        actions.appendChild(termBtn);

        const vscodeBtn = document.createElement('button');
        vscodeBtn.className = 'btn-vscode';
        vscodeBtn.textContent = 'VSCode';
        vscodeBtn.onclick = () => openProjectIDE(proj.slug, 'vscode');
        actions.appendChild(vscodeBtn);

        const cursorBtn = document.createElement('button');
        cursorBtn.className = 'btn-cursor';
        cursorBtn.textContent = 'Cursor';
        cursorBtn.onclick = () => openProjectIDE(proj.slug, 'cursor');
        actions.appendChild(cursorBtn);

        if (proj.html_url) {
            const htmlLink = document.createElement('a');
            htmlLink.href = proj.html_url;
            htmlLink.target = '_blank';
            htmlLink.className = 'btn-secondary';
            htmlLink.textContent = 'Open HTML ↗';
            actions.appendChild(htmlLink);
        }

        const footer = document.createElement('div');
        footer.className = 'project-footer';
        footer.textContent = `Last synced: ${proj.last_synced_at ? new Date(proj.last_synced_at).toLocaleString('ko-KR') : 'Never'}`;

        card.appendChild(desc);
        card.appendChild(techDiv);
        if (badgesDiv) { card.appendChild(badgesDiv); }
        card.appendChild(actions);
        card.appendChild(footer);
        grid.appendChild(card);
    });
}

function renderRecentActivity(activity) {
    const list = document.getElementById('recentList');
    list.textContent = '';

    activity.forEach(commit => {
        const item = document.createElement('div');
        item.className = 'recent-item';
        item.onclick = function() {
            window.location.href = '/project.html?slug=' + encodeURIComponent(commit.project_slug);
        };

        const date = document.createElement('div');
        date.className = 'recent-date';
        date.textContent = commit.date;

        const project = document.createElement('div');
        project.className = 'recent-project';
        project.textContent = commit.project_name;

        const type = document.createElement('div');
        type.className = `recent-type type-${commit.type}`;
        type.textContent = commit.type;

        const title = document.createElement('div');
        title.className = 'recent-title';
        title.textContent = commit.title;

        item.appendChild(date);
        item.appendChild(project);
        item.appendChild(type);
        item.appendChild(title);
        list.appendChild(item);
    });
}

async function openProjectFolder(slug) {
    try {
        const res = await fetch(`${API_BASE}/api/projects/${slug}/open-folder`, { method: 'POST' });
        if (!res.ok) throw new Error('Failed to open folder');
    } catch (error) {
        alert('폴더 열기 실패: ' + error.message);
    }
}

async function openProjectTerminal(slug) {
    try {
        const res = await fetch(`${API_BASE}/api/projects/${slug}/open-terminal`, { method: 'POST' });
        if (!res.ok) throw new Error('Failed to open terminal');
    } catch (error) {
        alert('터미널 열기 실패: ' + error.message);
    }
}

async function openProjectIDE(slug, ide) {
    try {
        const res = await fetch(`${API_BASE}/api/projects/${slug}/open-${ide}`, { method: 'POST' });
        if (!res.ok) throw new Error(`Failed to open ${ide}`);
    } catch (error) {
        alert(`${ide} 열기 실패: ` + error.message);
    }
}

function reloadData() {
    loadDashboard();
}

async function triggerSync() {
    const btn = document.querySelector('.sync-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Syncing...';
    }
    try {
        const res = await fetch(`${API_BASE}/api/sync`, { method: 'POST' });
        if (!res.ok) throw new Error('Sync failed');
        const result = await res.json();
        loadDashboard();
        if (btn) btn.textContent = `Synced (${result.projects_synced} projects)`;
        setTimeout(() => { if (btn) { btn.textContent = 'Sync'; btn.disabled = false; } }, 2000);
    } catch (error) {
        console.error('Sync failed:', error);
        alert('Sync failed: ' + error.message);
        if (btn) { btn.textContent = 'Sync'; btn.disabled = false; }
    }
}

// Load on page load
if (document.getElementById('projectsGrid')) {
    loadDashboard();
}
