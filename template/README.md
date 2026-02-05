# Dev Log System Template

각 프로젝트에 개발 로그 시스템을 설치하는 템플릿

## 빠른 시작

### 1. 새 프로젝트에 설치

```bash
cd your-project/
~/dev-log-template/install-devlog.sh
```

대화형으로 프로젝트 정보를 입력하면 자동으로 설치됩니다.

### 2. 첫 로그 작성

```bash
./scripts/dev-log.sh "feat: initial setup"
```

### 3. HTML 생성

```bash
./scripts/update-html.sh
```

### 4. 확인

```bash
open docs/html/index.html
```

---

## 상세 가이드

### 설치 스크립트가 하는 일

`install-devlog.sh` 실행 시:

1. ✅ 디렉토리 생성
   - `docs/dev-log/` - 마크다운 원본
   - `docs/html/` - 생성된 HTML
   - `scripts/` - 생성 스크립트

2. ✅ 파일 복사
   - Python 생성 스크립트 (9개)
   - Shell 스크립트 (2개)
   - CSS, JavaScript

3. ✅ 초기 데이터 생성
   - `docs/html/data/dev-logs.json`
   - `docs/html/README.md`

4. ✅ Git 설정
   - `.gitignore` 업데이트

5. ✅ 통합 어드민 연동
   - `~/dev-log-admin/config.json`에 자동 추가
   - SQLite DB 동기화

### 설치 후 디렉토리 구조

```
your-project/
├── docs/
│   ├── dev-log/              # 마크다운 원본
│   │   └── *.md
│   └── html/                 # 생성된 HTML
│       ├── index.html        # Kanban Board
│       ├── timeline.html     # Timeline
│       ├── heatmap.html      # Heatmap
│       ├── files.html        # File History
│       ├── commit-size.html  # Commit Size
│       ├── time-analysis.html # Time Analysis
│       ├── deployment.html   # Deployment
│       ├── stats.html        # Statistics
│       ├── styles.css        # 공통 스타일
│       ├── scripts.js        # 공통 JavaScript
│       └── data/
│           └── dev-logs.json # 데이터
└── scripts/
    ├── dev-log.sh           # 로그 작성
    ├── update-html.sh       # HTML 생성
    ├── parse-devlog.py      # 파싱
    └── generate-*.py        # 각 페이지 생성
```

---

## 사용 방법

### 개발 로그 작성

```bash
# 기본 사용
./scripts/dev-log.sh "feat: add new feature"

# 타입 지정
./scripts/dev-log.sh "fix: bug fix"
./scripts/dev-log.sh "docs: update README"
./scripts/dev-log.sh "refactor: improve code"
./scripts/dev-log.sh "test: add tests"
./scripts/dev-log.sh "chore: update deps"
./scripts/dev-log.sh "ci: update workflow"
```

### HTML 재생성

```bash
./scripts/update-html.sh
```

9개 페이지가 순차적으로 생성됩니다.

### 통합 어드민에서 확인

```bash
# 어드민 서버 실행 (한 번만)
cd ~/dev-log-admin
python server.py

# 브라우저에서
open http://localhost:8100
```

---

## 업데이트

dev-log 시스템 업데이트 시:

```bash
cd your-project/
~/dev-log-template/update-devlog.sh
```

- ✅ 스크립트만 업데이트
- ✅ 기존 데이터 보존
- ✅ 자동 백업 생성

---

## 여러 프로젝트 관리

### 구조

```
~/01_DEV/
├── project-a/              # 독립 실행
│   └── docs/html/
├── project-b/              # 독립 실행
│   └── docs/html/
└── project-c/              # 독립 실행
    └── docs/html/

~/dev-log-admin/            # 통합 뷰
└── config.json             # 자동 추가됨
```

### 새 프로젝트 추가

```bash
cd ~/01_DEV/new-project/
~/dev-log-template/install-devlog.sh
```

자동으로 통합 어드민에 추가됩니다.

### 통합 어드민 동기화

```bash
cd ~/dev-log-admin
python sync.py
```

---

## Git 통합

### Commit Hook (선택)

자동으로 dev-log 생성:

```bash
# .git/hooks/post-commit
#!/bin/bash
COMMIT_MSG=$(git log -1 --pretty=%B)
./scripts/dev-log.sh "$COMMIT_MSG"
./scripts/update-html.sh
git add docs/html/data/dev-logs.json
git commit --amend --no-edit --no-verify
```

### .gitignore

HTML 파일은 선택적으로 커밋:

```gitignore
# dev-logs.json은 커밋 (데이터)
# HTML은 선택적 (주석 해제하면 제외)
# docs/html/*.html
```

---

## 문제 해결

### "Template not found"

```bash
# 템플릿이 없으면 현재 프로젝트에서 생성
cd ~/01_DEV/saas-ws-abada-co-kr
cp -r scripts ~/dev-log-template/
cp docs/html/styles.css ~/dev-log-template/
cp docs/html/scripts.js ~/dev-log-template/
```

### "dev-log-admin not found"

통합 어드민 없이도 각 프로젝트는 독립 실행 가능합니다.

### 데이터 손실 시

```bash
# Git 히스토리에서 복구
git checkout HEAD~1 -- docs/html/data/dev-logs.json
```

---

## 파일 설명

### 스크립트

- `install-devlog.sh` - 새 프로젝트 설치
- `update-devlog.sh` - 시스템 업데이트
- `scripts/dev-log.sh` - 로그 작성
- `scripts/update-html.sh` - HTML 생성
- `scripts/parse-devlog.py` - 마크다운 → JSON
- `scripts/generate-*.py` - 각 페이지 생성

### Static Files

- `styles.css` - 공통 스타일 (다크모드 포함)
- `scripts.js` - 공통 JavaScript

---

## 템플릿 업데이트

템플릿 자체 업데이트:

```bash
cd ~/01_DEV/saas-ws-abada-co-kr

# 최신 버전 복사
cp -r scripts ~/dev-log-template/
cp docs/html/styles.css ~/dev-log-template/
cp docs/html/scripts.js ~/dev-log-template/

# 모든 프로젝트 업데이트
cd ~/01_DEV/project-a && ~/dev-log-template/update-devlog.sh
cd ~/01_DEV/project-b && ~/dev-log-template/update-devlog.sh
```

---

## 지원

- 템플릿 위치: `~/dev-log-template/`
- 통합 어드민: `~/dev-log-admin/`
- 문서: 각 프로젝트 `docs/html/README.md`

---

**버전**: 1.0
**업데이트**: 2026-02-05
