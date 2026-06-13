# Scripts Directory

Dev Log 시스템의 스크립트 디렉토리입니다.

## Core Scripts

### dev-log.sh
Git 커밋 정보를 파싱하여 마크다운 개발 로그를 생성합니다.

```bash
./scripts/dev-log.sh              # HEAD 커밋 기준
./scripts/dev-log.sh abc1234      # 특정 커밋 기준
```

**Commit Types**: feat, fix, docs, refactor, test, chore, ci, style, perf, build, revert

---

### update-html.sh
모든 HTML 페이지를 순차적으로 생성합니다 (9단계).

```bash
./scripts/update-html.sh
```

**생성 순서**:
1. parse-devlog.py (JSON 파싱)
2. generate-html.py (Kanban Board)
3. generate-timeline.py (Timeline)
4. generate-heatmap.py (Heatmap)
5. generate-files-history.py (Files)
6. generate-commit-size.py (Commit Size)
7. generate-time-analysis.py (Time Analysis)
8. generate-deployment.py (Deployment)
9. generate-stats.py (Statistics)

---

## Python Scripts

| Script | Output | Description |
|--------|--------|-------------|
| `parse-devlog.py` | `dev-logs.json` | Markdown to JSON parser |
| `generate-html.py` | `index.html` | Kanban Board |
| `generate-timeline.py` | `timeline.html` | Timeline View |
| `generate-heatmap.py` | `heatmap.html` | Activity Heatmap |
| `generate-files-history.py` | `files.html` | File Change History |
| `generate-commit-size.py` | `commit-size.html` | Commit Size Analysis |
| `generate-time-analysis.py` | `time-analysis.html` | Time Pattern Analysis |
| `generate-deployment.py` | `deployment.html` | Deployment History |
| `generate-stats.py` | `stats.html` | Statistics |

---

## etc/

비 템플릿 참고용 파일들이 보관되어 있습니다.

---

## Script Permissions

```bash
chmod +x scripts/*.sh
```
