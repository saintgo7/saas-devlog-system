#!/bin/bash
#
# Dev Log System - Master Installer
# 전체 시스템을 한 번에 설치합니다
#

set -e

echo ""
echo "=========================================="
echo "📦 Dev Log System Installer"
echo "=========================================="
echo ""
echo "Version: 1.0"
echo "Author: Ph.D SNT Go."
echo ""

# 현재 디렉토리
INSTALL_DIR=$(cd "$(dirname "$0")" && pwd)

echo "📁 Installation package: $INSTALL_DIR"
echo ""

# 확인
read -p "Install Dev Log System? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "🔧 Installing Components..."
echo "=========================================="
echo ""

# 1. Template 설치
echo "📋 [1/3] Installing template..."
if [ -d ~/dev-log-template ]; then
    echo "   ⚠️  ~/dev-log-template already exists"
    read -p "   Overwrite? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf ~/dev-log-template
        cp -r "$INSTALL_DIR/template" ~/dev-log-template
        echo "   ✅ Template updated"
    else
        echo "   ⏭️  Skipped"
    fi
else
    cp -r "$INSTALL_DIR/template" ~/dev-log-template
    echo "   ✅ Template installed: ~/dev-log-template/"
fi

# 2. Admin 설치
echo ""
echo "🌐 [2/3] Installing admin..."
if [ -d ~/dev-log-admin ]; then
    echo "   ⚠️  ~/dev-log-admin already exists"
    read -p "   Overwrite? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 기존 config.json과 devlog.db 백업
        if [ -f ~/dev-log-admin/config.json ]; then
            cp ~/dev-log-admin/config.json ~/dev-log-admin/config.json.backup
            echo "   💾 Backed up config.json"
        fi
        if [ -f ~/dev-log-admin/devlog.db ]; then
            cp ~/dev-log-admin/devlog.db ~/dev-log-admin/devlog.db.backup
            echo "   💾 Backed up devlog.db"
        fi

        rm -rf ~/dev-log-admin
        cp -r "$INSTALL_DIR/admin" ~/dev-log-admin

        # 백업 복원
        if [ -f ~/dev-log-admin/config.json.backup ]; then
            mv ~/dev-log-admin/config.json.backup ~/dev-log-admin/config.json
            echo "   ♻️  Restored config.json"
        fi
        if [ -f ~/dev-log-admin/devlog.db.backup ]; then
            mv ~/dev-log-admin/devlog.db.backup ~/dev-log-admin/devlog.db
            echo "   ♻️  Restored devlog.db"
        fi

        echo "   ✅ Admin updated"
    else
        echo "   ⏭️  Skipped"
    fi
else
    cp -r "$INSTALL_DIR/admin" ~/dev-log-admin
    echo "   ✅ Admin installed: ~/dev-log-admin/"
fi

# 3. Claude integration 설치
echo ""
echo "🤖 [3/3] Installing Claude Code integration..."
mkdir -p ~/.claude/skills/dev-log

if [ -f ~/.claude/skills/dev-log/SKILL.md ]; then
    echo "   ⚠️  Skill already exists"
    read -p "   Overwrite? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$INSTALL_DIR/claude-integration/SKILL.md" ~/.claude/skills/dev-log/
        echo "   ✅ Skill updated"
    else
        echo "   ⏭️  Skipped"
    fi
else
    cp "$INSTALL_DIR/claude-integration/SKILL.md" ~/.claude/skills/dev-log/
    echo "   ✅ Skill installed: ~/.claude/skills/dev-log/"
fi

# Python 패키지 확인
echo ""
echo "=========================================="
echo "🐍 Checking Python packages..."
echo "=========================================="
echo ""

if command -v python3 >/dev/null 2>&1; then
    echo "✅ Python3 found: $(python3 --version)"

    # FastAPI 확인
    if python3 -c "import fastapi" 2>/dev/null; then
        echo "✅ FastAPI installed"
    else
        echo "⚠️  FastAPI not found"
        read -p "Install FastAPI? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip3 install fastapi uvicorn
            echo "✅ FastAPI installed"
        fi
    fi
else
    echo "⚠️  Python3 not found. Please install Python 3.8+"
fi

# 초기 설정
echo ""
echo "=========================================="
echo "⚙️  Initial Setup"
echo "=========================================="
echo ""

# Admin DB 초기화
if [ ! -f ~/dev-log-admin/devlog.db ]; then
    echo "📊 Initializing admin database..."
    (cd ~/dev-log-admin && python3 database.py)
else
    echo "✅ Admin database already exists"
fi

# 완료
echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📍 Installed Components:"
echo "   • Template: ~/dev-log-template/"
echo "   • Admin:    ~/dev-log-admin/"
echo "   • Skill:    ~/.claude/skills/dev-log/"
echo ""
echo "📍 Next Steps:"
echo ""
echo "1. Install to a project:"
echo "   cd your-project/"
echo "   ~/dev-log-template/install-devlog.sh"
echo ""
echo "2. Start admin server:"
echo "   cd ~/dev-log-admin"
echo "   python3 server.py"
echo "   # http://localhost:8100"
echo ""
echo "3. Documentation:"
echo "   ~/dev-log-system/docs/QUICKSTART.md"
echo ""
echo "🎉 Enjoy Dev Log System!"
echo ""
