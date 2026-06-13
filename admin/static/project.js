// Project Detail Page JavaScript
const API_BASE = '';

const TYPE_COLORS = {
    'feat': '#10b981', 'fix': '#ef4444', 'refactor': '#8b5cf6',
    'docs': '#3b82f6', 'test': '#f59e0b', 'chore': '#6b7280',
    'ci': '#06b6d4', 'perf': '#ec4899'
};

let currentSlug = '';
let currentOffset = 0;
let currentTotal = 0;
let activeTypeFilter = '';
let searchQuery = '';
const COMMITS_LIMIT = 50;

function getSlugFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('slug') || '';
}

async function loadProject(slug) {
    try {
        const [projectRes, commitsRes, statsRes, deployRes, previewRes] = await Promise.all([
            fetch(`${API_BASE}/api/projects/${encodeURIComponent(slug)}`),
            fetch(`${API_BASE}/api/projects/${encodeURIComponent(slug)}/commits?limit=${COMMITS_LIMIT}&offset=0`),
            fetch(`${API_BASE}/api/projects/${encodeURIComponent(slug)}/stats`),
            fetch(`${API_BASE}/api/projects/${encodeURIComponent(slug)}/deployment-info`),
            fetch(`${API_BASE}/api/projects/${encodeURIComponent(slug)}/preview-info`)
        ]);

        if (!projectRes.ok) {
            throw new Error('Project not found');
        }

        const project = await projectRes.json();
        const commitsData = await commitsRes.json();
        const stats = statsRes.ok ? await statsRes.json() : null;
        const deployData = deployRes.ok ? await deployRes.json() : null;
        const previewData = previewRes.ok ? await previewRes.json() : null;

        currentTotal = commitsData.total;
        currentOffset = commitsData.commits.length;

        document.title = `Dev Log Admin - ${project.name}`;
        document.getElementById('projectTitle').textContent = project.name;

        renderProjectInfo(project);
        renderProjectStats(project, stats);
        if (deployData) { renderDeploymentInfo(deployData); }
        if (previewData) { renderPreviewSection(previewData); }
        renderTypeFilters(project.type_stats || {});
        renderCommits(commitsData.commits, false);
        updateLoadMoreButton();

    } catch (error) {
        console.error('Failed to load project:', error);
        var container = document.getElementById('projectInfo');
        container.textContent = '';
        var errorDiv = document.createElement('div');
        errorDiv.className = 'project-detail-error';
        errorDiv.textContent = 'Project not found or failed to load.';
        container.appendChild(errorDiv);
    }
}

function renderProjectInfo(project) {
    const container = document.getElementById('projectInfo');
    container.textContent = '';
    container.className = 'project-detail-header';

    const infoTop = document.createElement('div');
    infoTop.className = 'project-detail-top';

    const descDiv = document.createElement('div');
    descDiv.className = 'project-detail-desc';

    if (project.description) {
        const desc = document.createElement('p');
        desc.textContent = project.description;
        descDiv.appendChild(desc);
    }

    const techDiv = document.createElement('div');
    techDiv.className = 'project-tech';
    (project.tech_stack || []).forEach(function(tech) {
        const tag = document.createElement('span');
        tag.className = 'tech-tag';
        tag.textContent = tech;
        techDiv.appendChild(tag);
    });
    descDiv.appendChild(techDiv);
    infoTop.appendChild(descDiv);

    const linksDiv = document.createElement('div');
    linksDiv.className = 'project-detail-links';
    linksDiv.style.display = 'flex';
    linksDiv.style.flexWrap = 'wrap';
    linksDiv.style.gap = '0.5rem';
    linksDiv.style.alignItems = 'center';

    if (project.repository_url) {
        const repoLink = document.createElement('a');
        repoLink.href = project.repository_url;
        repoLink.target = '_blank';
        repoLink.className = 'btn-secondary';
        repoLink.textContent = 'Repository';
        linksDiv.appendChild(repoLink);
    }

    if (project.html_url) {
        const htmlLink = document.createElement('a');
        htmlLink.href = project.html_url;
        htmlLink.target = '_blank';
        htmlLink.className = 'btn-secondary';
        htmlLink.textContent = 'Open HTML';
        linksDiv.appendChild(htmlLink);
    }

    const folderBtn = document.createElement('button');
    folderBtn.className = 'btn-folder';
    folderBtn.textContent = 'Open Folder';
    folderBtn.onclick = function() { openProjectFolder(currentSlug); };
    linksDiv.appendChild(folderBtn);

    const termBtn = document.createElement('button');
    termBtn.className = 'btn-terminal';
    termBtn.textContent = 'Terminal';
    termBtn.onclick = function() { openProjectTerminal(currentSlug); };
    linksDiv.appendChild(termBtn);

    const vscodeBtn = document.createElement('button');
    vscodeBtn.className = 'btn-vscode';
    vscodeBtn.textContent = 'VSCode';
    vscodeBtn.onclick = function() { openProjectIDE(currentSlug, 'vscode'); };
    linksDiv.appendChild(vscodeBtn);

    const cursorBtn = document.createElement('button');
    cursorBtn.className = 'btn-cursor';
    cursorBtn.textContent = 'Cursor';
    cursorBtn.onclick = function() { openProjectIDE(currentSlug, 'cursor'); };
    linksDiv.appendChild(cursorBtn);

    const syncInfo = document.createElement('span');
    syncInfo.className = 'project-detail-sync';
    syncInfo.textContent = 'Last synced: ' +
        (project.last_synced_at ? new Date(project.last_synced_at).toLocaleString('ko-KR') : 'Never');
    linksDiv.appendChild(syncInfo);

    infoTop.appendChild(linksDiv);
    container.appendChild(infoTop);
}

function renderProjectStats(project, statsData) {
    const container = document.getElementById('projectStats');
    container.textContent = '';

    var statCards = [
        { label: 'Total Commits', value: project.total_commits || 0 },
        { label: 'Tech Stack', value: (project.tech_stack || []).length },
        { label: 'Commit Types', value: Object.keys(project.type_stats || {}).length }
    ];

    // Add stats from /api/projects/{slug}/stats if available
    if (statsData) {
        statCards.push({ label: 'Total Lines Added', value: statsData.total_lines_added || 0 });
        statCards.push({ label: 'Total Lines Deleted', value: statsData.total_lines_deleted || 0 });
        statCards.push({ label: 'Total Files Changed', value: statsData.total_files_changed || 0 });
        if (statsData.most_active_day) {
            statCards.push({ label: 'Most Active Day', value: statsData.most_active_day, isText: true });
        }
    }

    statCards.forEach(function(stat) {
        var card = document.createElement('div');
        card.className = 'stat-card';

        var label = document.createElement('div');
        label.className = 'stat-label';
        label.textContent = stat.label;

        var value = document.createElement('div');
        value.className = stat.isText ? 'stat-value-small' : 'stat-value';
        value.textContent = stat.isText ? stat.value : stat.value.toLocaleString();

        card.appendChild(label);
        card.appendChild(value);
        container.appendChild(card);
    });

    // Type distribution mini chart
    var typeStats = project.type_stats || {};
    if (Object.keys(typeStats).length > 0) {
        var chartCard = document.createElement('div');
        chartCard.className = 'stat-card stat-card-wide';

        var chartLabel = document.createElement('div');
        chartLabel.className = 'stat-label';
        chartLabel.textContent = 'Type Distribution';
        chartCard.appendChild(chartLabel);

        var chartBar = document.createElement('div');
        chartBar.className = 'type-dist-bar';

        var total = Object.values(typeStats).reduce(function(a, b) { return a + b; }, 0);

        Object.entries(typeStats)
            .sort(function(a, b) { return b[1] - a[1]; })
            .forEach(function(entry) {
                var type = entry[0];
                var count = entry[1];
                var pct = (count / total * 100);
                var seg = document.createElement('div');
                seg.className = 'type-dist-segment';
                seg.style.width = pct + '%';
                seg.style.backgroundColor = TYPE_COLORS[type] || '#6b7280';
                seg.title = type + ': ' + count + ' (' + pct.toFixed(1) + '%)';
                chartBar.appendChild(seg);
            });

        chartCard.appendChild(chartBar);

        var legend = document.createElement('div');
        legend.className = 'type-dist-legend';
        Object.entries(typeStats)
            .sort(function(a, b) { return b[1] - a[1]; })
            .forEach(function(entry) {
                var type = entry[0];
                var count = entry[1];
                var item = document.createElement('span');
                item.className = 'type-dist-legend-item';

                var dot = document.createElement('span');
                dot.className = 'type-dist-dot';
                dot.style.backgroundColor = TYPE_COLORS[type] || '#6b7280';

                item.appendChild(dot);
                item.appendChild(document.createTextNode(type + ' (' + count + ')'));
                legend.appendChild(item);
            });
        chartCard.appendChild(legend);

        container.appendChild(chartCard);
    }

    // Commits by month horizontal bar chart
    if (statsData && statsData.commits_by_month && Object.keys(statsData.commits_by_month).length > 0) {
        var monthCard = document.createElement('div');
        monthCard.className = 'stat-card stat-card-wide';

        var monthLabel = document.createElement('div');
        monthLabel.className = 'stat-label';
        monthLabel.textContent = 'Commits by Month (Last 6 Months)';
        monthCard.appendChild(monthLabel);

        var monthChart = document.createElement('div');
        monthChart.className = 'type-chart';
        monthChart.style.marginTop = '0.75rem';

        var maxCount = Math.max.apply(null, Object.values(statsData.commits_by_month));

        Object.entries(statsData.commits_by_month).forEach(function(entry) {
            var month = entry[0];
            var count = entry[1];
            var pct = maxCount > 0 ? (count / maxCount * 100) : 0;

            var barDiv = document.createElement('div');
            barDiv.className = 'type-bar';

            var labelDiv = document.createElement('div');
            labelDiv.className = 'type-label';

            var nameSpan = document.createElement('span');
            nameSpan.className = 'type-name';
            nameSpan.textContent = month;

            var countSpan = document.createElement('span');
            countSpan.className = 'type-count';
            countSpan.textContent = count + ' commits';

            labelDiv.appendChild(nameSpan);
            labelDiv.appendChild(countSpan);

            var progressDiv = document.createElement('div');
            progressDiv.className = 'type-progress';

            var fillDiv = document.createElement('div');
            fillDiv.className = 'type-fill';
            fillDiv.style.width = pct + '%';
            fillDiv.style.backgroundColor = '#667eea';

            progressDiv.appendChild(fillDiv);
            barDiv.appendChild(labelDiv);
            barDiv.appendChild(progressDiv);
            monthChart.appendChild(barDiv);
        });

        monthCard.appendChild(monthChart);
        container.appendChild(monthCard);
    }
}

// Platform badge color mapping
const PLATFORM_STYLES = {
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

const WORKFLOW_TYPE_COLORS = {
    'deploy': '#10b981',
    'ci': '#3b82f6',
    'test': '#f59e0b',
};

function renderDeploymentInfo(data) {
    var section = document.getElementById('deploymentInfo');
    section.textContent = '';

    var hasPlatforms = data.platforms && data.platforms.length > 0;
    var hasDomains = data.domains && data.domains.length > 0;
    var hasCiCd = data.ci_cd && data.ci_cd.workflows && data.ci_cd.workflows.length > 0;
    var hasGit = data.git_status && data.git_status.current_branch;

    if (!hasPlatforms && !hasDomains && !hasCiCd && !hasGit) {
        return; // Nothing to show
    }

    section.style.display = 'block';

    // Section title
    var title = document.createElement('h2');
    title.className = 'deploy-section-title';
    title.textContent = 'Deployment & Infrastructure';
    section.appendChild(title);

    var grid = document.createElement('div');
    grid.className = 'deploy-info-grid';

    // Card 1: Platforms & Domains
    if (hasPlatforms || hasDomains) {
        var card1 = document.createElement('div');
        card1.className = 'deploy-card';

        var card1Title = document.createElement('div');
        card1Title.className = 'deploy-card-title';
        card1Title.textContent = 'Platforms & Domains';
        card1.appendChild(card1Title);

        if (hasPlatforms) {
            var platformsDiv = document.createElement('div');
            platformsDiv.className = 'deploy-platforms';
            data.platforms.forEach(function(p) {
                var badge = document.createElement('span');
                badge.className = 'platform-badge';
                var style = PLATFORM_STYLES[p] || { bg: '#6b7280', color: '#ffffff' };
                badge.style.backgroundColor = style.bg;
                badge.style.color = style.color;
                badge.textContent = p;
                platformsDiv.appendChild(badge);
            });
            card1.appendChild(platformsDiv);
        }

        if (hasDomains) {
            var domainsDiv = document.createElement('div');
            domainsDiv.className = 'deploy-domains';
            var domainsLabel = document.createElement('div');
            domainsLabel.className = 'deploy-sub-label';
            domainsLabel.textContent = 'Domains';
            domainsDiv.appendChild(domainsLabel);
            data.domains.forEach(function(d) {
                var tag = document.createElement('span');
                tag.className = 'domain-tag';
                tag.textContent = d;
                domainsDiv.appendChild(tag);
            });
            card1.appendChild(domainsDiv);
        }

        grid.appendChild(card1);
    }

    // Card 2: CI/CD Pipelines
    if (hasCiCd) {
        var card2 = document.createElement('div');
        card2.className = 'deploy-card';

        var card2Title = document.createElement('div');
        card2Title.className = 'deploy-card-title';
        card2Title.textContent = 'CI/CD Pipelines';
        card2.appendChild(card2Title);

        var wfList = document.createElement('div');
        wfList.className = 'workflow-list';
        data.ci_cd.workflows.forEach(function(wf) {
            var item = document.createElement('div');
            item.className = 'workflow-item';

            var dot = document.createElement('span');
            dot.className = 'workflow-type-dot';
            dot.style.backgroundColor = WORKFLOW_TYPE_COLORS[wf.type] || '#6b7280';

            var name = document.createElement('span');
            name.className = 'workflow-name';
            name.textContent = wf.name;

            var typeLabel = document.createElement('span');
            typeLabel.className = 'workflow-type-label';
            typeLabel.textContent = wf.type;

            item.appendChild(dot);
            item.appendChild(name);
            item.appendChild(typeLabel);
            wfList.appendChild(item);
        });
        card2.appendChild(wfList);
        grid.appendChild(card2);
    }

    // Card 3: Git Status
    if (hasGit) {
        var gs = data.git_status;
        var card3 = document.createElement('div');
        card3.className = 'deploy-card';

        var card3Title = document.createElement('div');
        card3Title.className = 'deploy-card-title';
        card3Title.textContent = 'Git Status';
        card3.appendChild(card3Title);

        var gitItems = document.createElement('div');
        gitItems.className = 'git-status-list';

        // Branch
        var branchItem = document.createElement('div');
        branchItem.className = 'git-status-item';
        var branchLabel = document.createElement('span');
        branchLabel.className = 'git-status-label';
        branchLabel.textContent = 'Branch';
        var branchValue = document.createElement('span');
        branchValue.className = 'git-branch-badge';
        branchValue.textContent = gs.current_branch;
        branchItem.appendChild(branchLabel);
        branchItem.appendChild(branchValue);
        gitItems.appendChild(branchItem);

        // Uncommitted
        if (gs.uncommitted_count > 0) {
            var ucItem = document.createElement('div');
            ucItem.className = 'git-status-item';
            var ucLabel = document.createElement('span');
            ucLabel.className = 'git-status-label';
            ucLabel.textContent = 'Uncommitted';
            var ucValue = document.createElement('span');
            ucValue.className = 'git-warning';
            ucValue.textContent = gs.uncommitted_count + ' changes';
            ucItem.appendChild(ucLabel);
            ucItem.appendChild(ucValue);
            gitItems.appendChild(ucItem);
        }

        // Ahead/Behind
        if (gs.ahead > 0 || gs.behind > 0) {
            var abItem = document.createElement('div');
            abItem.className = 'git-status-item';
            var abLabel = document.createElement('span');
            abLabel.className = 'git-status-label';
            abLabel.textContent = 'Sync';
            var abValue = document.createElement('span');
            abValue.className = (gs.ahead > 0 || gs.behind > 0) ? 'git-warning' : 'git-ok';
            var parts = [];
            if (gs.ahead > 0) parts.push(gs.ahead + ' ahead');
            if (gs.behind > 0) parts.push(gs.behind + ' behind');
            abValue.textContent = parts.join(', ');
            abItem.appendChild(abLabel);
            abItem.appendChild(abValue);
            gitItems.appendChild(abItem);
        }

        // Branch count
        if (gs.branches && gs.branches.length > 1) {
            var brCountItem = document.createElement('div');
            brCountItem.className = 'git-status-item';
            var brCountLabel = document.createElement('span');
            brCountLabel.className = 'git-status-label';
            brCountLabel.textContent = 'Branches';
            var brCountValue = document.createElement('span');
            brCountValue.className = 'git-ok';
            brCountValue.textContent = gs.branches.length + ' (' + gs.branches.join(', ') + ')';
            brCountItem.appendChild(brCountLabel);
            brCountItem.appendChild(brCountValue);
            gitItems.appendChild(brCountItem);
        }

        // Last commit
        if (gs.last_commit) {
            var lcItem = document.createElement('div');
            lcItem.className = 'git-status-item';
            var lcLabel = document.createElement('span');
            lcLabel.className = 'git-status-label';
            lcLabel.textContent = 'Last Commit';
            var lcValue = document.createElement('span');
            lcValue.className = 'git-status-value';
            lcValue.textContent = gs.last_commit.hash + ' ' + gs.last_commit.message;
            lcItem.appendChild(lcLabel);
            lcItem.appendChild(lcValue);
            gitItems.appendChild(lcItem);
        }

        // Remote URL
        if (gs.remote_url) {
            var remoteItem = document.createElement('div');
            remoteItem.className = 'git-status-item';
            var remoteLabel = document.createElement('span');
            remoteLabel.className = 'git-status-label';
            remoteLabel.textContent = 'Remote';
            var remoteValue = document.createElement('span');
            remoteValue.className = 'git-status-value git-remote-url';
            remoteValue.textContent = gs.remote_url;
            remoteItem.appendChild(remoteLabel);
            remoteItem.appendChild(remoteValue);
            gitItems.appendChild(remoteItem);
        }

        card3.appendChild(gitItems);
        grid.appendChild(card3);
    }

    section.appendChild(grid);
}

function renderPreviewSection(data) {
    if (!data || !data.previews || data.previews.length === 0) {
        return;
    }

    var deploySection = document.getElementById('deploymentInfo');
    var commitsSection = deploySection.parentNode.querySelector('.section');

    var section = document.createElement('section');
    section.className = 'preview-section';
    section.id = 'previewSection';

    // Title bar
    var titleBar = document.createElement('div');
    titleBar.className = 'preview-title-bar';

    var title = document.createElement('h2');
    title.textContent = 'Site Preview';
    titleBar.appendChild(title);

    var controls = document.createElement('div');
    controls.className = 'preview-controls';

    // Toggle buttons for each preview type
    data.previews.forEach(function(preview, index) {
        var btn = document.createElement('button');
        btn.className = 'preview-toggle-btn' + (index === 0 ? ' active' : '');
        btn.textContent = preview.label;
        btn.setAttribute('data-preview-url', preview.url);
        btn.onclick = function() {
            switchPreview(preview.url);
            var allBtns = section.querySelectorAll('.preview-toggle-btn');
            allBtns.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
        };
        controls.appendChild(btn);
    });

    // Fullscreen button
    var fsBtn = document.createElement('button');
    fsBtn.className = 'preview-action-btn';
    fsBtn.textContent = 'Fullscreen';
    fsBtn.onclick = function() { togglePreviewFullscreen(); };
    controls.appendChild(fsBtn);

    // Open in new tab
    var newTabLink = document.createElement('a');
    newTabLink.className = 'preview-action-btn';
    newTabLink.id = 'previewNewTabLink';
    newTabLink.href = data.previews[0].url;
    newTabLink.target = '_blank';
    newTabLink.textContent = 'Open in Tab';
    controls.appendChild(newTabLink);

    titleBar.appendChild(controls);
    section.appendChild(titleBar);

    // iframe container
    var iframeContainer = document.createElement('div');
    iframeContainer.className = 'preview-iframe-container';
    iframeContainer.id = 'previewIframeContainer';

    var exitFsBtn = document.createElement('button');
    exitFsBtn.className = 'preview-exit-fullscreen';
    exitFsBtn.textContent = 'Exit Fullscreen';
    exitFsBtn.onclick = function() { togglePreviewFullscreen(); };
    iframeContainer.appendChild(exitFsBtn);

    var iframe = document.createElement('iframe');
    iframe.className = 'preview-iframe';
    iframe.id = 'previewIframe';
    iframe.src = data.previews[0].url;
    iframe.loading = 'lazy';
    iframe.sandbox = 'allow-scripts allow-same-origin allow-popups';
    iframe.title = 'Site Preview';
    iframeContainer.appendChild(iframe);

    section.appendChild(iframeContainer);

    // Insert after deploymentInfo, before commits section
    deploySection.parentNode.insertBefore(section, commitsSection);
}

function switchPreview(url) {
    var iframe = document.getElementById('previewIframe');
    if (iframe) {
        iframe.src = url;
    }
    var newTabLink = document.getElementById('previewNewTabLink');
    if (newTabLink) {
        newTabLink.href = url;
    }
}

function togglePreviewFullscreen() {
    var container = document.getElementById('previewIframeContainer');
    if (container) {
        container.classList.toggle('preview-fullscreen');
    }
}

function renderTypeFilters(typeStats) {
    var container = document.getElementById('typeFilters');
    container.textContent = '';

    var allBtn = document.createElement('button');
    allBtn.className = 'type-filter-btn' + (activeTypeFilter === '' ? ' active' : '');
    allBtn.textContent = 'All';
    allBtn.onclick = function() {
        activeTypeFilter = '';
        currentOffset = 0;
        reloadCommits();
    };
    container.appendChild(allBtn);

    Object.entries(typeStats)
        .sort(function(a, b) { return b[1] - a[1]; })
        .forEach(function(entry) {
            var type = entry[0];
            var count = entry[1];
            var btn = document.createElement('button');
            btn.className = 'type-filter-btn type-' + type + (activeTypeFilter === type ? ' active' : '');
            btn.textContent = type + ' (' + count + ')';
            btn.onclick = function() {
                activeTypeFilter = type;
                currentOffset = 0;
                reloadCommits();
            };
            container.appendChild(btn);
        });
}

function renderCommits(commits, append) {
    var container = document.getElementById('commitsList');
    if (!append) {
        container.textContent = '';
    }

    if (commits.length === 0 && !append) {
        var empty = document.createElement('div');
        empty.className = 'commits-empty';
        empty.textContent = 'No commits found.';
        container.appendChild(empty);
        return;
    }

    commits.forEach(function(commit) {
        var item = document.createElement('div');
        item.className = 'commit-item';
        item.onclick = function() { openCommitModal(commit.id); };

        var left = document.createElement('div');
        left.className = 'commit-item-left';

        var typeBadge = document.createElement('span');
        typeBadge.className = 'commit-type-badge type-' + commit.type;
        typeBadge.textContent = commit.type;

        var title = document.createElement('span');
        title.className = 'commit-title';
        title.textContent = commit.title;

        left.appendChild(typeBadge);
        left.appendChild(title);

        var right = document.createElement('div');
        right.className = 'commit-item-right';

        var meta = document.createElement('span');
        meta.className = 'commit-meta';
        var filesChanged = commit.files_changed || 0;
        var linesAdded = commit.lines_added || 0;
        var linesDeleted = commit.lines_deleted || 0;
        meta.textContent = filesChanged + ' files';
        if (linesAdded > 0 || linesDeleted > 0) {
            meta.textContent += '  +' + linesAdded + ' -' + linesDeleted;
        }

        var date = document.createElement('span');
        date.className = 'commit-date';
        date.textContent = commit.date;

        right.appendChild(meta);
        right.appendChild(date);

        item.appendChild(left);
        item.appendChild(right);
        container.appendChild(item);
    });
}

async function reloadCommits() {
    var url = API_BASE + '/api/projects/' + encodeURIComponent(currentSlug)
        + '/commits?limit=' + COMMITS_LIMIT + '&offset=0';

    if (activeTypeFilter) {
        url += '&type=' + encodeURIComponent(activeTypeFilter);
    }
    if (searchQuery) {
        url += '&search=' + encodeURIComponent(searchQuery);
    }

    try {
        var res = await fetch(url);
        var data = await res.json();
        currentTotal = data.total;
        currentOffset = data.commits.length;
        renderCommits(data.commits, false);
        updateLoadMoreButton();
        updateFilterButtons();
    } catch (error) {
        console.error('Failed to reload commits:', error);
    }
}

async function loadMoreCommits() {
    var url = API_BASE + '/api/projects/' + encodeURIComponent(currentSlug)
        + '/commits?limit=' + COMMITS_LIMIT + '&offset=' + currentOffset;

    if (activeTypeFilter) {
        url += '&type=' + encodeURIComponent(activeTypeFilter);
    }
    if (searchQuery) {
        url += '&search=' + encodeURIComponent(searchQuery);
    }

    try {
        var res = await fetch(url);
        var data = await res.json();
        currentOffset += data.commits.length;
        renderCommits(data.commits, true);
        updateLoadMoreButton();
    } catch (error) {
        console.error('Failed to load more commits:', error);
    }
}

function updateLoadMoreButton() {
    var container = document.getElementById('loadMoreContainer');
    container.style.display = currentOffset < currentTotal ? 'flex' : 'none';
}

function updateFilterButtons() {
    var buttons = document.querySelectorAll('.type-filter-btn');
    buttons.forEach(function(btn) {
        btn.classList.remove('active');
    });
    buttons.forEach(function(btn) {
        var text = btn.textContent;
        if (activeTypeFilter === '' && text === 'All') {
            btn.classList.add('active');
        } else if (text.startsWith(activeTypeFilter + ' ')) {
            btn.classList.add('active');
        }
    });
}

async function openCommitModal(commitId) {
    var modal = document.getElementById('commitModal');
    var body = document.getElementById('modalBody');
    var titleEl = document.getElementById('modalTitle');

    modal.style.display = 'flex';
    body.textContent = '';
    var loadingDiv = document.createElement('div');
    loadingDiv.className = 'commit-modal-loading';
    loadingDiv.textContent = 'Loading...';
    body.appendChild(loadingDiv);
    titleEl.textContent = 'Commit Detail';

    try {
        var res = await fetch(API_BASE + '/api/commits/' + commitId);
        var commit = await res.json();

        titleEl.textContent = commit.title;
        body.textContent = '';

        // Meta info
        var metaSection = document.createElement('div');
        metaSection.className = 'modal-meta';

        var items = [
            { label: 'Type', value: commit.type, className: 'type-' + commit.type },
            { label: 'Date', value: commit.date },
            { label: 'Files Changed', value: (commit.files_changed || 0).toString() },
            { label: 'Lines', value: '+' + (commit.lines_added || 0) + ' / -' + (commit.lines_deleted || 0) }
        ];

        items.forEach(function(item) {
            var row = document.createElement('div');
            row.className = 'modal-meta-item';

            var label = document.createElement('span');
            label.className = 'modal-meta-label';
            label.textContent = item.label;

            var value = document.createElement('span');
            value.className = 'modal-meta-value';
            if (item.className) {
                value.classList.add(item.className);
            }
            value.textContent = item.value;

            row.appendChild(label);
            row.appendChild(value);
            metaSection.appendChild(row);
        });
        body.appendChild(metaSection);

        // Full content
        if (commit.full_content) {
            var contentSection = document.createElement('div');
            contentSection.className = 'modal-content-section';

            var contentLabel = document.createElement('h4');
            contentLabel.textContent = 'Full Content';
            contentSection.appendChild(contentLabel);

            var pre = document.createElement('pre');
            pre.className = 'modal-content-pre';
            pre.textContent = commit.full_content;
            contentSection.appendChild(pre);

            body.appendChild(contentSection);
        }

    } catch (error) {
        console.error('Failed to load commit detail:', error);
        body.textContent = 'Failed to load commit details.';
    }
}

function closeCommitModal() {
    document.getElementById('commitModal').style.display = 'none';
}

// Close modal or fullscreen on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        var container = document.getElementById('previewIframeContainer');
        if (container && container.classList.contains('preview-fullscreen')) {
            container.classList.remove('preview-fullscreen');
            return;
        }
        closeCommitModal();
    }
});

// Debounced commit search
var searchTimeout = null;
document.getElementById('commitSearch').addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() {
        searchQuery = e.target.value.trim();
        currentOffset = 0;
        reloadCommits();
    }, 300);
});

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

// Initialize
currentSlug = getSlugFromUrl();
if (currentSlug) {
    loadProject(currentSlug);
} else {
    var container = document.getElementById('projectInfo');
    container.textContent = '';
    var errorDiv = document.createElement('div');
    errorDiv.className = 'project-detail-error';
    var errorText = document.createTextNode('No project slug specified. ');
    var backLink = document.createElement('a');
    backLink.href = '/';
    backLink.textContent = 'Back to Dashboard';
    errorDiv.appendChild(errorText);
    errorDiv.appendChild(backLink);
    container.appendChild(errorDiv);
}
