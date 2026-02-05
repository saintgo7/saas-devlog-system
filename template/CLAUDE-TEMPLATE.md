# Dev Log System - CLAUDE.md Template

프로젝트 CLAUDE.md에 추가할 내용

---

## Dev Log System (개발 로그 시스템)

이 프로젝트는 자동 개발 로그 시스템을 사용합니다.

### 명령어

#### 개발 로그 작성
```bash
./scripts/dev-log.sh "feat: add new feature"
./scripts/dev-log.sh "fix: bug fix"
./scripts/dev-log.sh "docs: update documentation"
```

**지원하는 타입:**
- `feat` - 새 기능
- `fix` - 버그 수정
- `refactor` - 리팩토링
- `docs` - 문서
- `test` - 테스트
- `chore` - 기타 작업
- `ci` - CI/CD
- `perf` - 성능 개선

#### HTML 생성
```bash
./scripts/update-html.sh
```

9개 페이지 생성:
1. index.html - Kanban Board
2. timeline.html - Timeline View
3. heatmap.html - Commit Heatmap
4. files.html - File Change History
5. commit-size.html - Commit Size Analysis
6. time-analysis.html - Time-based Analysis
7. deployment.html - Deployment History
8. stats.html - Statistics

#### 확인
```bash
open docs/html/index.html
```

### Claude Code 사용 시

**개발 로그 자동 작성:**
```
User: "feat 추가했어"
Claude: ./scripts/dev-log.sh "feat: [내용]" 실행 후 HTML 생성
```

**작업 완료 시 자동:**
1. 작업 완료
2. Git 커밋
3. Dev log 작성
4. HTML 생성

### 디렉토리 구조

```
docs/
├── dev-log/              # 마크다운 원본 (Git 관리)
│   └── *.md
└── html/                 # 생성된 HTML
    ├── index.html
    ├── data/dev-logs.json  # 데이터 소스
    └── ...
```

### 금지 사항

- `docs/html/data/dev-logs.json` 직접 수정 금지
- HTML 파일 직접 수정 금지 (생성 스크립트 사용)
- dev-log 삭제 시 반드시 사용자 확인 필요

### 통합 어드민

여러 프로젝트를 한눈에 보려면:
```bash
cd ~/dev-log-admin
python server.py
# http://localhost:8100
```

---

## CLAUDE.md에 추가하는 방법

프로젝트의 `CLAUDE.md` 또는 `.claude/CLAUDE.md`에 위 내용을 추가하세요.

### 예시

```markdown
# My Project - Claude Code 설정

## Dev Log System

이 프로젝트는 자동 개발 로그 시스템을 사용합니다.

### 작업 완료 시 프로세스

1. 코드 작성/수정
2. 테스트
3. Git 커밋
4. **Dev log 작성** ← Claude가 자동으로
   ```bash
   ./scripts/dev-log.sh "feat: 작업 내용"
   ./scripts/update-html.sh
   ```
5. Git add & commit (dev-log 포함)

### 명령어
- Dev log 작성: `./scripts/dev-log.sh "type: message"`
- HTML 생성: `./scripts/update-html.sh`
- 확인: `open docs/html/index.html`

### 주의사항
- dev-log는 주요 작업 완료 시에만 작성
- 커밋 메시지와 dev-log 내용 일치
- JSON 파일 직접 수정 금지
```

---

## 자동화 예시

### Git Hook (선택)

`.git/hooks/post-commit`:
```bash
#!/bin/bash
COMMIT_MSG=$(git log -1 --pretty=%B)
./scripts/dev-log.sh "$COMMIT_MSG"
./scripts/update-html.sh
git add docs/html/data/dev-logs.json docs/html/*.html
git commit --amend --no-edit --no-verify
```

### Claude Code 워크플로우

Claude Code가 다음을 자동으로:
1. 작업 완료 감지
2. Dev log 작성 제안
3. HTML 생성
4. Git 커밋 (선택적)

---

## 팁

- **작은 작업도 로그 남기기**: 나중에 유용
- **일관된 포맷 사용**: type: description 형식
- **자주 HTML 생성**: 변경사항 즉시 확인
- **통합 어드민 활용**: 여러 프로젝트 비교

---

**설치**: `~/dev-log-template/install-devlog.sh`
**문서**: `docs/html/README.md`
