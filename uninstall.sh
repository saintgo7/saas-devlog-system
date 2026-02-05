#!/bin/bash
#
# Dev Log System - Uninstaller
# 시스템 제거
#

set -e

echo ""
echo "=========================================="
echo "🗑️  Dev Log System Uninstaller"
echo "=========================================="
echo ""

# 경고
echo "⚠️  WARNING: This will remove:"
echo "   • ~/dev-log-template/"
echo "   • ~/dev-log-admin/"
echo "   • ~/.claude/skills/dev-log/"
echo ""
echo "⚠️  Your project dev-logs will NOT be removed"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "🗑️  Removing components..."
echo ""

# Template 제거
if [ -d ~/dev-log-template ]; then
    rm -rf ~/dev-log-template
    echo "✅ Removed ~/dev-log-template/"
else
    echo "⏭️  Template not found"
fi

# Admin 제거 (백업 옵션)
if [ -d ~/dev-log-admin ]; then
    read -p "Backup admin data before removing? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        BACKUP_DIR=~/dev-log-admin-backup-$(date +%Y%m%d-%H%M%S)
        mkdir -p "$BACKUP_DIR"
        [ -f ~/dev-log-admin/config.json ] && cp ~/dev-log-admin/config.json "$BACKUP_DIR/"
        [ -f ~/dev-log-admin/devlog.db ] && cp ~/dev-log-admin/devlog.db "$BACKUP_DIR/"
        echo "   💾 Backup created: $BACKUP_DIR"
    fi

    rm -rf ~/dev-log-admin
    echo "✅ Removed ~/dev-log-admin/"
else
    echo "⏭️  Admin not found"
fi

# Claude skill 제거
if [ -d ~/.claude/skills/dev-log ]; then
    rm -rf ~/.claude/skills/dev-log
    echo "✅ Removed ~/.claude/skills/dev-log/"
else
    echo "⏭️  Skill not found"
fi

echo ""
echo "=========================================="
echo "✅ Uninstall Complete"
echo "=========================================="
echo ""
echo "📍 Note:"
echo "   Your project dev-logs are still intact"
echo "   (project/docs/dev-log/ and project/docs/html/)"
echo ""
echo "📍 To remove from a project:"
echo "   cd your-project/"
echo "   rm -rf docs/dev-log/ docs/html/ scripts/"
echo ""
