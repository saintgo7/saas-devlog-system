// Search page JavaScript
const API_BASE = '';
const SEARCH_LIMIT = 100;

let currentQuery = '';
let currentProject = '';
let currentType = '';
let currentOffset = 0;
let currentTotal = 0;

// Load projects for the filter dropdown
async function loadProjects() {
    try {
        const res = await fetch(`${API_BASE}/api/projects`);
        const data = await res.json();
        const select = document.getElementById('projectFilter');
        const projects = Array.isArray(data) ? data : (data.projects || []);
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.slug;
            option.textContent = project.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load projects:', error);
    }
}

// Read URL params and populate filters
function readUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q') || '';
    const project = params.get('project') || '';
    const type = params.get('type') || '';

    document.getElementById('searchInput').value = q;
    currentQuery = q;

    if (project) {
        document.getElementById('projectFilter').value = project;
        currentProject = project;
    }

    if (type) {
        currentType = type;
        updateTypeFilterButtons();
    }

    return q || project || type;
}

// Update URL to reflect current filter state
function updateUrl() {
    const params = new URLSearchParams();
    if (currentQuery) params.set('q', currentQuery);
    if (currentProject) params.set('project', currentProject);
    if (currentType) params.set('type', currentType);

    const newUrl = params.toString()
        ? `${window.location.pathname}?${params.toString()}`
        : window.location.pathname;
    history.replaceState(null, '', newUrl);
}

// Update active state on type filter buttons
function updateTypeFilterButtons() {
    document.querySelectorAll('#typeFilters .type-filter-btn').forEach(btn => {
        const btnType = btn.getAttribute('data-type');
        btn.classList.toggle('active', btnType === currentType);
    });
}

// Build search API URL (q is always sent; empty string matches all)
function buildSearchUrl(offset) {
    let url = `${API_BASE}/api/search?q=${encodeURIComponent(currentQuery)}&limit=${SEARCH_LIMIT}&offset=${offset}`;
    if (currentProject) url += `&project=${encodeURIComponent(currentProject)}`;
    if (currentType) url += `&type=${encodeURIComponent(currentType)}`;
    return url;
}

// Perform search (resets offset)
async function performSearch() {
    currentQuery = document.getElementById('searchInput').value.trim();
    currentProject = document.getElementById('projectFilter').value;
    currentOffset = 0;

    updateUrl();

    if (!currentQuery && !currentProject && !currentType) {
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.textContent = '';
        const hint = document.createElement('p');
        hint.className = 'search-hint';
        hint.textContent = '검색어를 입력하거나 필터를 선택하세요';
        resultsDiv.appendChild(hint);
        hideLoadMore();
        return;
    }

    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.textContent = '검색 중...';

    try {
        const res = await fetch(buildSearchUrl(0));
        const data = await res.json();

        currentTotal = data.total;
        currentOffset = data.results.length;

        resultsDiv.textContent = '';

        if (data.total === 0) {
            const noResults = document.createElement('p');
            noResults.className = 'no-results';
            noResults.textContent = '검색 결과가 없습니다';
            resultsDiv.appendChild(noResults);
            hideLoadMore();
            return;
        }

        const summary = document.createElement('p');
        summary.className = 'search-summary';
        summary.textContent = `${data.total}개의 결과를 찾았습니다`;
        resultsDiv.appendChild(summary);

        const list = document.createElement('div');
        list.id = 'resultsList';
        resultsDiv.appendChild(list);

        renderResults(data.results, list);
        updateLoadMore();

    } catch (error) {
        console.error('Search failed:', error);
        resultsDiv.textContent = '검색 실패: ' + error.message;
    }
}

// Load more results
async function loadMore() {
    try {
        const res = await fetch(buildSearchUrl(currentOffset));
        const data = await res.json();

        currentOffset += data.results.length;

        const list = document.getElementById('resultsList');
        if (list) {
            renderResults(data.results, list);
        }
        updateLoadMore();

    } catch (error) {
        console.error('Load more failed:', error);
    }
}

// Render search result items into a container
function renderResults(results, container) {
    results.forEach(commit => {
        const item = document.createElement('div');
        item.className = 'search-result-item search-result-clickable';
        item.onclick = () => {
            window.location.href = `/project.html?slug=${encodeURIComponent(commit.project_slug || commit.project_name)}`;
        };

        const header = document.createElement('div');
        header.className = 'result-header';

        const project = document.createElement('span');
        project.className = 'result-project';
        project.textContent = commit.project_name;

        const type = document.createElement('span');
        type.className = `result-type type-${commit.type}`;
        type.textContent = commit.type;

        const date = document.createElement('span');
        date.className = 'result-date';
        date.textContent = commit.date;

        header.appendChild(project);
        header.appendChild(type);
        header.appendChild(date);

        const title = document.createElement('h4');
        title.className = 'result-title';
        title.textContent = commit.title;

        const meta = document.createElement('div');
        meta.className = 'result-meta';
        meta.textContent = `${commit.files_changed || 0} files, +${commit.lines_added || 0} -${commit.lines_deleted || 0}`;

        item.appendChild(header);
        item.appendChild(title);
        item.appendChild(meta);
        container.appendChild(item);
    });
}

// Show/hide load more button
function updateLoadMore() {
    const btn = document.getElementById('loadMoreBtn');
    btn.style.display = currentOffset < currentTotal ? 'block' : 'none';
}

function hideLoadMore() {
    document.getElementById('loadMoreBtn').style.display = 'none';
}

// --- Event Listeners ---

// Enter key search
document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

// Project filter change
document.getElementById('projectFilter').addEventListener('change', () => {
    performSearch();
});

// Type filter button clicks
document.querySelectorAll('#typeFilters .type-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        currentType = btn.getAttribute('data-type');
        updateTypeFilterButtons();
        performSearch();
    });
});

// --- Initialize ---
(async function init() {
    await loadProjects();
    const hasParams = readUrlParams();
    if (hasParams) {
        // Re-set project value after projects are loaded
        if (currentProject) {
            document.getElementById('projectFilter').value = currentProject;
        }
        performSearch();
    }
})();
