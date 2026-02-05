#!/bin/bash
#
# Dev Log System Updater
# 기존 프로젝트의 dev-log 시스템을 최신 버전으로 업데이트합니다
#

set -e

echo ""
echo "=========================================="
echo "🔄 Dev Log System Updater"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
CURRENT_DIR=$(pwd)
PROJECT_NAME=$(basename "$CURRENT_DIR")

if [ ! -d "docs/html" ]; then
    echo "❌ Error: docs/html not found"
    echo "   This doesn't look like a dev-log project"
    echo "   Run install-devlog.sh first"
    exit 1
fi

echo "📁 Project: $PROJECT_NAME"
echo "📂 Location: $CURRENT_DIR"
echo ""

# 백업 생성
echo "💾 Creating backup..."
BACKUP_DIR="docs/html-backup-$(date +%Y%m%d-%H%M%S)"
cp -r docs/html "$BACKUP_DIR"
echo "   Backup created: $BACKUP_DIR"
echo ""

# 템플릿 디렉토리
TEMPLATE_DIR=~/dev-log-template

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "❌ Error: Template not found at $TEMPLATE_DIR"
    exit 1
fi

# Scripts 업데이트
echo "📋 Updating scripts..."
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
echo "   ✅ Scripts updated"

# Static files 업데이트
echo "🎨 Updating static files..."
cp "$TEMPLATE_DIR"/styles.css docs/html/
cp "$TEMPLATE_DIR"/scripts.js docs/html/
echo "   ✅ Static files updated"

# 기존 데이터 보존
echo "💾 Preserving existing data..."
if [ -f "docs/html/data/dev-logs.json" ]; then
    echo "   ✅ dev-logs.json preserved"
else
    echo "   ⚠️  dev-logs.json not found"
fi

# HTML 재생성
echo ""
read -p "Regenerate HTML files? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔨 Regenerating HTML..."
    ./scripts/update-html.sh
    echo "   ✅ HTML regenerated"
fi

echo ""
echo "=========================================="
echo "✅ Update Complete!"
echo "=========================================="
echo ""
echo "📍 What was updated:"
echo "   • Python scripts (generate-*.py)"
echo "   • Shell scripts (*.sh)"
echo "   • CSS styles"
echo "   • JavaScript"
echo ""
echo "📍 What was preserved:"
echo "   • docs/html/data/dev-logs.json"
echo "   • docs/dev-log/*.md"
echo ""
echo "📍 Backup location:"
echo "   $BACKUP_DIR"
echo ""
