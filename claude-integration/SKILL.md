# Dev Log Skill

Development logging skill with automated HTML visualization system.

## Trigger Keywords
- "dev log", "devlog", "development log"
- "create log", "add log", "write log"
- "log this", "record this"
- "generate html", "update html"
- "install devlog", "setup devlog"

## System Overview

This project uses an automated dev-log system:
- **Markdown logs**: `docs/dev-log/*.md`
- **HTML visualization**: `docs/html/*.html`
- **Data file**: `docs/html/data/dev-logs.json`

## Commands

### 1. Create Dev Log

```bash
./scripts/dev-log.sh "type: description"
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `docs` - Documentation
- `test` - Tests
- `chore` - Maintenance
- `ci` - CI/CD
- `perf` - Performance

**Example:**
```bash
./scripts/dev-log.sh "feat: add user authentication"
./scripts/dev-log.sh "fix: resolve login bug"
```

### 2. Generate HTML

```bash
./scripts/update-html.sh
```

Generates 8 visualization pages:
1. **index.html** - Kanban Board with filters
2. **timeline.html** - Chronological timeline
3. **heatmap.html** - Activity heatmap
4. **files.html** - File change history
5. **commit-size.html** - Commit size analysis
6. **time-analysis.html** - Time patterns
7. **deployment.html** - Deployment history
8. **stats.html** - Statistics dashboard

### 3. View Logs

```bash
open docs/html/index.html
```

Or integrated admin (if installed):
```bash
http://localhost:8100
```

## Installation

### For New Projects

```bash
cd your-project/
~/dev-log-template/install-devlog.sh
```

Interactive setup:
- Project name
- Description
- Repository URL
- Tech stack

**Auto-configures:**
- Directory structure
- Scripts
- Git ignore
- Integration with admin

### For Existing Projects

```bash
cd your-project/
~/dev-log-template/update-devlog.sh
```

## Workflow

### When Task is Completed

1. Write code/make changes
2. Test
3. Git commit
4. **Create dev log**:
   ```bash
   ./scripts/dev-log.sh "feat: implemented X"
   ```
5. **Generate HTML**:
   ```bash
   ./scripts/update-html.sh
   ```
6. Review: `open docs/html/index.html`
7. Git commit (dev-log files)

### Claude Code Auto-Workflow

When Claude completes a task:

1. **Ask user**: "Create dev log for this work?"
2. **Execute**: `./scripts/dev-log.sh "type: description"`
3. **Generate**: `./scripts/update-html.sh`
4. **Show**: Link to HTML file
5. **Commit**: Include in git commit

## File Structure

```
project/
├── docs/
│   ├── dev-log/              # Markdown logs (commit to git)
│   │   └── *.md
│   └── html/                 # Generated HTML
│       ├── index.html
│       ├── timeline.html
│       ├── heatmap.html
│       ├── files.html
│       ├── commit-size.html
│       ├── time-analysis.html
│       ├── deployment.html
│       ├── stats.html
│       └── data/
│           └── dev-logs.json  # Data source
└── scripts/
    ├── dev-log.sh           # Create log
    ├── update-html.sh       # Generate HTML
    ├── parse-devlog.py      # Parse markdown
    └── generate-*.py        # Generate each page
```

## Auto-Logging Triggers

Create dev log when:
- ✅ Feature completed
- ✅ Bug fixed
- ✅ Refactoring done
- ✅ Tests added/updated
- ✅ Documentation updated
- ✅ Deployment completed
- ✅ Phase/milestone completed

## Best Practices

### 1. Descriptive Titles
```bash
# Good
./scripts/dev-log.sh "feat: add JWT authentication with refresh tokens"

# Bad
./scripts/dev-log.sh "feat: update"
```

### 2. Consistent Format
Always use: `type: description`

### 3. Frequent HTML Generation
Generate HTML after each log to track progress.

### 4. Git Integration
Commit dev-logs with related code changes:
```bash
git add .
git commit -m "feat: add authentication

- Implement JWT tokens
- Add refresh token logic
- Update tests"

./scripts/dev-log.sh "feat: add JWT authentication"
./scripts/update-html.sh
git add docs/
git commit -m "docs: update dev-log"
```

## Integration with Claude Code

### In CLAUDE.md

Add to project's `CLAUDE.md`:

```markdown
## Dev Log System

### After completing tasks:
1. Create dev log: `./scripts/dev-log.sh "type: description"`
2. Generate HTML: `./scripts/update-html.sh`
3. Commit: Include in git commit

### Commands:
- Create: `./scripts/dev-log.sh "feat: description"`
- Generate: `./scripts/update-html.sh`
- View: `open docs/html/index.html`
```

## Multi-Project Management

### Integrated Admin

If `~/dev-log-admin/` is installed:

```bash
cd ~/dev-log-admin
python server.py
# http://localhost:8100
```

**Features:**
- View all projects in one dashboard
- Search across all projects
- Compare project statistics
- Timeline view across projects

### Adding Projects

New projects auto-register during installation:
```bash
cd new-project/
~/dev-log-template/install-devlog.sh
# Auto-added to admin
```

## Troubleshooting

### "Template not found"

```bash
# Create template from existing project
cd ~/01_DEV/saas-ws-abada-co-kr
cp -r scripts ~/dev-log-template/
cp docs/html/styles.css ~/dev-log-template/
cp docs/html/scripts.js ~/dev-log-template/
```

### "Command not found"

```bash
chmod +x scripts/*.sh
```

### Data loss

Git tracks all logs:
```bash
git checkout HEAD~1 -- docs/html/data/dev-logs.json
```

## Commands for Claude

### Check if dev-log installed
```bash
[ -f "./scripts/dev-log.sh" ] && echo "installed" || echo "not installed"
```

### Create log
```bash
./scripts/dev-log.sh "feat: {description}"
```

### Generate HTML
```bash
./scripts/update-html.sh
```

### View
```bash
open docs/html/index.html
```

## Notes

- **Don't edit JSON directly**: Use scripts only
- **Don't edit HTML directly**: Regenerate with scripts
- **Commit markdown logs**: Essential history
- **HTML is optional**: Can regenerate anytime
- **Use consistent types**: feat, fix, refactor, docs, test, chore, ci, perf

## Resources

- Template: `~/dev-log-template/`
- Admin: `~/dev-log-admin/`
- Docs: `docs/html/README.md`
- Quick Start: `~/dev-log-template/QUICKSTART.md`
