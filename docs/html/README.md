# Dev Log - Dev Log System

개발 로그 시각화 시스템

## 사용 방법

### 1. 개발 로그 작성

```bash
./scripts/dev-log.sh "feat: add new feature"
```

### 2. HTML 생성

```bash
./scripts/update-html.sh
```

### 3. 확인

```bash
open docs/html/index.html
```

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

```bash
# 커밋 후 자동으로 dev-log 생성 (Git hook)
# .git/hooks/post-commit 설정 참고
```
