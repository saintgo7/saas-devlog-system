#!/bin/bash
#
# Dev Log System Installer
# 현재 프로젝트에 dev-log 시스템을 설치합니다
#

set -e

echo ""
echo "=========================================="
echo "📝 Dev Log System Installer"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
CURRENT_DIR=$(pwd)
PROJECT_NAME=$(basename "$CURRENT_DIR")

echo "📁 Current project: $PROJECT_NAME"
echo "📂 Location: $CURRENT_DIR"
echo ""

# Git 저장소 확인
if [ ! -d ".git" ]; then
    echo "⚠️  Warning: Not a git repository"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 프로젝트 정보 입력
echo "🔧 Project Setup"
echo "----------------"
read -p "Project name [$PROJECT_NAME]: " INPUT_NAME
PROJECT_DISPLAY_NAME=${INPUT_NAME:-$PROJECT_NAME}

read -p "Description: " PROJECT_DESC
read -p "Repository URL (optional): " REPO_URL

# Tech stack 입력
echo ""
echo "Tech stack (comma-separated, e.g., Python,FastAPI,React):"
read -p "> " TECH_STACK

# 디렉토리 생성
echo ""
echo "📁 Creating directories..."
mkdir -p docs/dev-log
mkdir -p docs/html/data
mkdir -p scripts

# 파일 복사
echo "📋 Copying files..."
TEMPLATE_DIR=~/dev-log-template

# Scripts
cp "$TEMPLATE_DIR"/scripts/parse-devlog.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-html.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-timeline.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-heatmap.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-stats.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-files-history.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-commit-size.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-time-analysis.py scripts/
cp "$TEMPLATE_DIR"/scripts/generate-deployment.py scripts/
cp "$TEMPLATE_DIR"/scripts/update-html.sh scripts/
cp "$TEMPLATE_DIR"/scripts/dev-log.sh scripts/
chmod +x scripts/*.sh

# Static files
cp "$TEMPLATE_DIR"/styles.css docs/html/
cp "$TEMPLATE_DIR"/scripts.js docs/html/

# 초기 dev-logs.json 생성
echo "📄 Creating initial dev-logs.json..."
cat > docs/html/data/dev-logs.json << EOF
{
  "statistics": {
    "total_logs": 0,
    "logs_by_type": {}
  },
  "logs": [],
  "generated_at": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

# README 생성
echo "📝 Creating README..."
cat > docs/html/README.md << EOF
# Dev Log - $PROJECT_DISPLAY_NAME

개발 로그 시각화 시스템

## 사용 방법

### 1. 개발 로그 작성

\`\`\`bash
./scripts/dev-log.sh "feat: add new feature"
\`\`\`

### 2. HTML 생성

\`\`\`bash
./scripts/update-html.sh
\`\`\`

### 3. 확인

\`\`\`bash
open docs/html/index.html
\`\`\`

## 페이지

- **index.html** - Kanban Board
- **timeline.html** - Timeline View
- **heatmap.html** - Commit Heatmap
- **files.html** - File History
- **commit-size.html** - Commit Size Analysis
- **time-analysis.html** - Time-based Analysis
- **deployment.html** - Deployment History
- **stats.html** - Statistics

## 자동화

\`\`\`bash
# 커밋 후 자동으로 dev-log 생성 (Git hook)
# .git/hooks/post-commit 설정 참고
\`\`\`
EOF

# Git ignore 업데이트
echo ""
echo "📝 Updating .gitignore..."
if [ -f ".gitignore" ]; then
    # dev-logs.json은 커밋, HTML은 선택적
    if ! grep -q "docs/html/\*.html" .gitignore 2>/dev/null; then
        echo "" >> .gitignore
        echo "# Dev Log (HTML files are optional)" >> .gitignore
        echo "# docs/html/*.html" >> .gitignore
    fi
else
    cat > .gitignore << EOF
# Dev Log (HTML files are optional)
# docs/html/*.html
EOF
fi

# 통합 어드민에 추가
echo ""
echo "🔗 Adding to dev-log-admin..."
ADMIN_CONFIG=~/dev-log-admin/config.json

if [ -f "$ADMIN_CONFIG" ]; then
    # Python으로 JSON 업데이트
    python3 << PYTHON
import json
import os

config_path = os.path.expanduser('$ADMIN_CONFIG')
project_dir = '$CURRENT_DIR'

with open(config_path, 'r') as f:
    config = json.load(f)

# 프로젝트 슬러그 생성
slug = '$PROJECT_NAME'.lower().replace(' ', '-').replace('_', '-')

# 이미 있는지 확인
existing = [p for p in config['projects'] if p['slug'] == slug]

if not existing:
    new_project = {
        'slug': slug,
        'name': '$PROJECT_DISPLAY_NAME',
        'description': '$PROJECT_DESC',
        'repository_url': '$REPO_URL',
        'tech_stack': ['$TECH_STACK'.replace(',', '","').strip() for item in '$TECH_STACK'.split(',') if item.strip()],
        'json_path': project_dir + '/docs/html/data/dev-logs.json',
        'html_url': 'file://' + project_dir + '/docs/html/index.html'
    }
    config['projects'].append(new_project)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Added '{slug}' to dev-log-admin")
else:
    print(f"⚠️  Project '{slug}' already exists in dev-log-admin")
PYTHON

    # 동기화
    if command -v python3 >/dev/null 2>&1; then
        echo "🔄 Syncing to admin database..."
        (cd ~/dev-log-admin && python3 sync.py) || echo "⚠️  Sync failed (run manually later)"
    fi
else
    echo "⚠️  dev-log-admin not found at ~/dev-log-admin"
    echo "   Install manually or skip integration"
fi

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📍 Next steps:"
echo ""
echo "1. Create your first dev log:"
echo "   ./scripts/dev-log.sh \"feat: initial setup\""
echo ""
echo "2. Generate HTML:"
echo "   ./scripts/update-html.sh"
echo ""
echo "3. View in browser:"
echo "   open docs/html/index.html"
echo ""
echo "4. (Optional) View in admin:"
echo "   http://localhost:8100"
echo ""
echo "📚 Documentation: docs/html/README.md"
echo ""
