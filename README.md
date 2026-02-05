# Dev Log System

*Read this in other languages: [English](README.md), [한국어](README.ko.md)*

Automated development log generation and visualization system

**Version**: 1.0
**Author**: Ph.D SNT Go.
**License**: MIT

---

## 🎯 Overview

A system that automatically tracks and visualizes development history for each project.

### Key Features

- ✅ **Automated Log Generation**: Write development logs with simple commands
- ✅ **8 Visualizations**: Kanban, Timeline, Heatmap, Files, Size, Time, Deployment, Stats
- ✅ **Unified Management**: Manage multiple projects in a single dashboard
- ✅ **Claude Code Integration**: AI-assisted automatic logging
- ✅ **Git Integration**: Version control with development history
- ✅ **Independent Operation**: Each project operates independently
- ✅ **SQLite-based**: Lightweight database

---

## 🚀 Quick Start

### 1. System Installation (1 minute)

```bash
git clone https://github.com/saintgo7/saas-devlog-system.git
cd saas-devlog-system
./install.sh
```

What gets installed:
- `~/dev-log-template/` - Project templates
- `~/dev-log-admin/` - Integrated admin dashboard
- `~/.claude/skills/dev-log/` - Claude Code skill

### 2. Project Installation (1 minute)

```bash
cd your-project/
~/dev-log-template/install-devlog.sh
```

Interactive setup prompts you for project information.

### 3. Usage

```bash
# Write development log
./scripts/dev-log.sh "feat: add new feature"

# Generate HTML
./scripts/update-html.sh

# View
open docs/html/index.html
```

---

## 📦 Package Structure

```
dev-log-system/
├── README.md              # This file
├── install.sh             # Master installation script
├── template/              # Per-project templates
│   ├── scripts/           # Python generation scripts (9 files)
│   ├── styles.css         # CSS
│   ├── scripts.js         # JavaScript
│   ├── install-devlog.sh  # Project installation script
│   ├── update-devlog.sh   # Update script
│   └── README.md          # Template documentation
├── admin/                 # Integrated admin
│   ├── server.py          # FastAPI server
│   ├── sync.py            # Synchronization script
│   ├── database.py        # SQLite initialization
│   ├── config.json        # Project configuration
│   ├── static/            # Frontend
│   └── README.md          # Admin documentation
├── claude-integration/    # Claude Code integration
│   ├── SKILL.md           # Skill definition
│   └── CLAUDE-TEMPLATE.md # Project CLAUDE.md template
└── docs/                  # Documentation
    ├── QUICKSTART.md      # Quick start guide
    └── ARCHITECTURE.md    # Architecture analysis
```

---

## 🎨 Visualization Pages

8 HTML pages generated for each project:

1. **index.html** - Kanban Board
   - Type filtering
   - Search functionality
   - Bookmarks
   - Advanced search

2. **timeline.html** - Timeline View
   - Chronological sorting
   - Date grouping
   - Detailed information

3. **heatmap.html** - Activity Heatmap
   - Monthly/daily activity
   - Color coding
   - Pattern analysis

4. **files.html** - File Change History
   - File-level change tracking
   - Category classification
   - Hot files analysis

5. **commit-size.html** - Commit Size Analysis
   - Commit size distribution
   - Best practices
   - Recommendations

6. **time-analysis.html** - Time-based Analysis
   - Hourly patterns
   - Day-of-week analysis
   - Productivity insights

7. **deployment.html** - Deployment History
   - Deployment history
   - CI/CD analysis
   - Frequency tracking

8. **stats.html** - Statistics Dashboard
   - Overall statistics
   - Type distribution
   - Trend analysis

---

## 🌐 Integrated Admin

View multiple projects at a glance:

```bash
cd ~/dev-log-admin
python3 server.py
# http://localhost:8100
```

**Features:**
- All-projects dashboard
- Unified search
- Cross-project comparison
- Real-time synchronization

---

## 🤖 Claude Code Integration

Claude Code automatically:
- Detects task completion
- Suggests dev log creation
- Generates HTML
- Includes in git commits

**Trigger Keywords:**
- "dev log 작성" (write dev log)
- "로그 남겨줘" (leave a log)
- "HTML 생성" (generate HTML)
- "devlog 설치" (install devlog)

---

## 📖 System Workflow

### Individual Project

```
1. Write code
2. Test
3. Git commit
4. ./scripts/dev-log.sh "type: description"
5. ./scripts/update-html.sh
6. open docs/html/index.html
```

### Unified Management

```
Multiple projects → dev-logs.json → SQLite → Unified dashboard
```

### Architecture

```
project-a/docs/html/         # Independent operation
project-b/docs/html/         # Independent operation
project-c/docs/html/         # Independent operation
        ↓
~/dev-log-admin/             # Unified view (optional)
```

---

## 🔧 Requirements

### Required
- Python 3.8+
- Git

### Optional (for integrated admin)
- FastAPI
- Uvicorn

Installation:
```bash
pip3 install fastapi uvicorn
```

---

## 📚 Documentation

- **Quick Start**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Template**: [template/README.md](template/README.md)
- **Admin**: [admin/README.md](admin/README.md)

---

## 🎯 Use Cases

### 1. Personal Projects
Track development history for each project

### 2. Team Collaboration
Unified management of multiple projects

### 3. Portfolio
Visualize development activities

### 4. Open Source
Share history alongside Git

### 5. Freelancing
Provide work history to clients

---

## 🌟 Key Features

### Independence
- Each project is fully independent
- Git clone includes dev-log
- Offline operation

### Scalability
- Easy project addition
- Unlimited projects
- Lightweight with SQLite

### Integration
- Claude Code automation
- Git integration
- Integrated admin provided

### Version Control
- Track history with Git
- Time travel capability
- Independent branches

---

## 🔄 Updates

### Template Update
```bash
cd your-project/
~/dev-log-template/update-devlog.sh
```

### System Reinstall
```bash
cd ~/saas-devlog-system
git pull
./install.sh
```

---

## 🐛 Troubleshooting

### "Template not found"
```bash
cd ~/saas-devlog-system
./install.sh
```

### "Python packages not found"
```bash
pip3 install fastapi uvicorn
```

### Data Loss
Recover with Git:
```bash
git checkout HEAD~1 -- docs/html/data/dev-logs.json
```

---

## 📊 Statistics

- **Code Size**: ~1,500 lines
- **Installation Time**: 1 minute
- **Project Addition**: 1 minute
- **Languages**: Python, Shell, JavaScript
- **Browsers**: Modern browsers

---

## 🎓 Lessons Learned

### Design Principles
1. **Distributed > Centralized**: Project independence
2. **Git = Backup**: No separate backup needed
3. **Static HTML**: Fast and stable
4. **SQLite**: Lightweight integration

### Tech Stack
- Python: Data processing
- JavaScript: Interaction
- CSS: Dark mode theme
- SQLite: Integrated DB
- FastAPI: REST API

---

## 📝 License

MIT License

Copyright (c) 2026 Ph.D SNT Go.

---

## 🤝 Contributing

Issues and PRs are welcome!

---

## 📧 Support

- GitHub: https://github.com/saintgo7/saas-devlog-system
- Issues: https://github.com/saintgo7/saas-devlog-system/issues
- Releases: https://github.com/saintgo7/saas-devlog-system/releases
- Docs: https://github.com/saintgo7/saas-devlog-system/tree/main/docs

---

## 🎉 Thank You!

Manage your development history systematically with Dev Log System!

**Enjoy coding!** 🚀
