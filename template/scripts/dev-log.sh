#!/bin/bash
#
# Development Log Generator (개발 로그 생성기)
# Automatically generates detailed development logs on git commit
#
# Usage: ./scripts/dev-log.sh [commit_hash]
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/docs/dev-log"
COUNTER_FILE="$LOG_DIR/.counter"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Get or initialize counter
get_counter() {
    if [ -f "$COUNTER_FILE" ]; then
        cat "$COUNTER_FILE"
    else
        echo "0"
    fi
}

increment_counter() {
    local current=$(get_counter)
    local next=$((current + 1))
    echo "$next" > "$COUNTER_FILE"
    printf "%03d" "$next"
}

# Get commit information
COMMIT_HASH="${1:-HEAD}"
COMMIT_SHORT=$(git rev-parse --short "$COMMIT_HASH" 2>/dev/null || echo "unknown")
COMMIT_MSG=$(git log -1 --format="%s" "$COMMIT_HASH" 2>/dev/null || echo "No commit message")
COMMIT_BODY=$(git log -1 --format="%b" "$COMMIT_HASH" 2>/dev/null || echo "")
COMMIT_AUTHOR=$(git log -1 --format="%an" "$COMMIT_HASH" 2>/dev/null || echo "Unknown")
COMMIT_EMAIL=$(git log -1 --format="%ae" "$COMMIT_HASH" 2>/dev/null || echo "")
COMMIT_DATE=$(git log -1 --format="%ai" "$COMMIT_HASH" 2>/dev/null || echo "")
# Cross-platform date parsing (git --format="%ai" outputs "YYYY-MM-DD HH:MM:SS +ZZZZ")
COMMIT_DATETIME=$(echo "$COMMIT_DATE" | sed 's/ [+-][0-9]*$//')
if [ -z "$COMMIT_DATETIME" ]; then
    COMMIT_DATETIME=$(date "+%Y-%m-%d %H:%M:%S")
fi
COMMIT_DATE_SHORT=$(echo "$COMMIT_DATETIME" | cut -c1-10)
COMMIT_TIME_SHORT=$(echo "$COMMIT_DATETIME" | cut -c12-13)$(echo "$COMMIT_DATETIME" | cut -c15-16)

# Extract commit type using sed
extract_commit_type() {
    local msg="$1"
    local type=$(echo "$msg" | sed -n 's/^\(feat\|fix\|docs\|style\|refactor\|test\|chore\|perf\|ci\|build\|revert\).*/\1/p')
    if [ -n "$type" ]; then
        echo "$type"
    else
        echo "other"
    fi
}

extract_commit_scope() {
    local msg="$1"
    local scope=$(echo "$msg" | sed -n 's/^[a-z]*(\([^)]*\)).*/\1/p')
    echo "$scope"
}

extract_commit_description() {
    local msg="$1"
    local desc=$(echo "$msg" | sed 's/^[a-z]*\(([^)]*)\)\?: *//')
    echo "$desc"
}

COMMIT_TYPE=$(extract_commit_type "$COMMIT_MSG")
COMMIT_SCOPE=$(extract_commit_scope "$COMMIT_MSG")
COMMIT_DESC=$(extract_commit_description "$COMMIT_MSG")

# Map commit type to Korean
type_to_korean() {
    case "$1" in
        feat) echo "기능 추가" ;;
        fix) echo "버그 수정" ;;
        docs) echo "문서 작업" ;;
        style) echo "코드 스타일" ;;
        refactor) echo "리팩토링" ;;
        test) echo "테스트" ;;
        chore) echo "기타 작업" ;;
        perf) echo "성능 개선" ;;
        ci) echo "CI/CD" ;;
        build) echo "빌드" ;;
        revert) echo "되돌리기" ;;
        *) echo "기타" ;;
    esac
}

COMMIT_TYPE_KR=$(type_to_korean "$COMMIT_TYPE")

# Get changed files
FILES_CHANGED=$(git diff-tree --no-commit-id --name-status -r "$COMMIT_HASH" 2>/dev/null || echo "")
FILES_SUMMARY=$(git diff-tree --no-commit-id --stat "$COMMIT_HASH" 2>/dev/null || echo "")
FILES_COUNT=$(echo "$FILES_CHANGED" | grep -c "." 2>/dev/null || echo "0")

# Get diff stats
DIFF_STATS=$(git show --stat --format="" "$COMMIT_HASH" 2>/dev/null | tail -1 || echo "")
ADDITIONS=$(echo "$DIFF_STATS" | grep -o '[0-9]* insertion' | grep -o '[0-9]*' || echo "0")
DELETIONS=$(echo "$DIFF_STATS" | grep -o '[0-9]* deletion' | grep -o '[0-9]*' || echo "0")

# Generate filename
COUNTER=$(increment_counter)
SAFE_DESC=$(echo "$COMMIT_DESC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)
LOG_FILENAME="${COUNTER}-${COMMIT_DATE_SHORT}-${COMMIT_TIME_SHORT}-${SAFE_DESC}.md"
LOG_PATH="$LOG_DIR/$LOG_FILENAME"

# Categorize changed files
generate_file_table() {
    echo ""

    # Backend files
    local backend=$(echo "$FILES_CHANGED" | grep "^[AMD].*server/" || true)
    if [ -n "$backend" ]; then
        echo ""
        echo "#### Backend (서버)"
        echo "| Status | File |"
        echo "|--------|------|"
        echo "$backend" | while IFS=$'\t' read -r status filepath; do
            case "$status" in
                A) icon="+" ;;
                M) icon="~" ;;
                D) icon="-" ;;
                *) icon="?" ;;
            esac
            echo "| \`$icon\` | \`$filepath\` |"
        done
    fi

    # Frontend files
    local frontend=$(echo "$FILES_CHANGED" | grep "^[AMD].*frontend/" || true)
    if [ -n "$frontend" ]; then
        echo ""
        echo "#### Frontend (프론트엔드)"
        echo "| Status | File |"
        echo "|--------|------|"
        echo "$frontend" | while IFS=$'\t' read -r status filepath; do
            case "$status" in
                A) icon="+" ;;
                M) icon="~" ;;
                D) icon="-" ;;
                *) icon="?" ;;
            esac
            echo "| \`$icon\` | \`$filepath\` |"
        done
    fi

    # Agent files
    local agent=$(echo "$FILES_CHANGED" | grep "^[AMD].*agent/" || true)
    if [ -n "$agent" ]; then
        echo ""
        echo "#### Agent (에이전트)"
        echo "| Status | File |"
        echo "|--------|------|"
        echo "$agent" | while IFS=$'\t' read -r status filepath; do
            case "$status" in
                A) icon="+" ;;
                M) icon="~" ;;
                D) icon="-" ;;
                *) icon="?" ;;
            esac
            echo "| \`$icon\` | \`$filepath\` |"
        done
    fi

    # Docs files
    local docs=$(echo "$FILES_CHANGED" | grep -E "^[AMD].*(docs/|\.md$)" || true)
    if [ -n "$docs" ]; then
        echo ""
        echo "#### Documentation (문서)"
        echo "| Status | File |"
        echo "|--------|------|"
        echo "$docs" | while IFS=$'\t' read -r status filepath; do
            case "$status" in
                A) icon="+" ;;
                M) icon="~" ;;
                D) icon="-" ;;
                *) icon="?" ;;
            esac
            echo "| \`$icon\` | \`$filepath\` |"
        done
    fi

    # Config files
    local config=$(echo "$FILES_CHANGED" | grep -E "^[AMD].*(\.yml$|\.yaml$|\.json$|\.env|Makefile|^\.[^/]+$)" || true)
    if [ -n "$config" ]; then
        echo ""
        echo "#### Configuration (설정)"
        echo "| Status | File |"
        echo "|--------|------|"
        echo "$config" | while IFS=$'\t' read -r status filepath; do
            case "$status" in
                A) icon="+" ;;
                M) icon="~" ;;
                D) icon="-" ;;
                *) icon="?" ;;
            esac
            echo "| \`$icon\` | \`$filepath\` |"
        done
    fi

    # Scripts
    local scripts=$(echo "$FILES_CHANGED" | grep "^[AMD].*scripts/" || true)
    if [ -n "$scripts" ]; then
        echo ""
        echo "#### Scripts (스크립트)"
        echo "| Status | File |"
        echo "|--------|------|"
        echo "$scripts" | while IFS=$'\t' read -r status filepath; do
            case "$status" in
                A) icon="+" ;;
                M) icon="~" ;;
                D) icon="-" ;;
                *) icon="?" ;;
            esac
            echo "| \`$icon\` | \`$filepath\` |"
        done
    fi
}

CATEGORIZED_FILES=$(generate_file_table)

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
PARENT_COMMIT=$(git log -1 --format="%P" "$COMMIT_HASH" 2>/dev/null | cut -c1-7 || echo "none")

# Generate scope line if exists
SCOPE_LINE=""
if [ -n "$COMMIT_SCOPE" ]; then
    SCOPE_LINE="**Scope**: ${COMMIT_SCOPE}"
fi

# Generate body section if exists
BODY_SECTION=""
if [ -n "$COMMIT_BODY" ]; then
    BODY_SECTION="### Details (상세 내용)

${COMMIT_BODY}"
fi

# Generate log content
cat > "$LOG_PATH" << EOF
# Development Log #${COUNTER} - ${COMMIT_DESC} (${COMMIT_TYPE_KR})

**Date**: ${COMMIT_DATETIME}
**Author**: ${COMMIT_AUTHOR} <${COMMIT_EMAIL}>
**Commit**: \`${COMMIT_SHORT}\`
**Type**: ${COMMIT_TYPE} (${COMMIT_TYPE_KR})
${SCOPE_LINE}

---

## Summary (요약)

${COMMIT_MSG}

${BODY_SECTION}

---

## Changes Overview (변경 개요)

| Metric | Value |
|--------|-------|
| Files Changed (변경된 파일) | ${FILES_COUNT} |
| Lines Added (추가된 라인) | +${ADDITIONS:-0} |
| Lines Deleted (삭제된 라인) | -${DELETIONS:-0} |

---

## Changed Files (변경된 파일)

Legend: \`+\` Added, \`~\` Modified, \`-\` Deleted
${CATEGORIZED_FILES}

---

## Technical Details (기술적 상세)

### Commit Statistics (커밋 통계)

\`\`\`
${FILES_SUMMARY}
\`\`\`

---

## Related Information (관련 정보)

- **Branch**: ${CURRENT_BRANCH}
- **Parent Commit**: ${PARENT_COMMIT}
- **Full Hash**: $(git rev-parse "$COMMIT_HASH" 2>/dev/null || echo "$COMMIT_HASH")

---

*Auto-generated by dev-log.sh on $(date "+%Y-%m-%d %H:%M:%S")*
*이 문서는 dev-log.sh에 의해 자동 생성되었습니다.*
EOF

echo -e "${GREEN}[dev-log]${NC} Created: ${LOG_FILENAME}"
echo -e "${GREEN}[dev-log]${NC} Path: ${LOG_PATH}"
