# Dev Log System - 빠른 시작 가이드

## 1분 설치 🚀

### 새 프로젝트에 설치

```bash
cd your-project/
~/dev-log-template/install-devlog.sh
```

**입력 사항:**
- Project name: (자동 감지)
- Description: 프로젝트 설명
- Repository URL: GitHub URL (선택)
- Tech stack: Python,FastAPI,React (쉼표로 구분)

**자동으로:**
- ✅ 디렉토리 생성
- ✅ 스크립트 복사
- ✅ 통합 어드민에 추가
- ✅ Git 설정

---

## 사용 예시

### 개발 로그 작성

```bash
# 새 기능 추가
./scripts/dev-log.sh "feat: add user authentication"

# 버그 수정
./scripts/dev-log.sh "fix: resolve login issue"

# 문서 업데이트
./scripts/dev-log.sh "docs: update API documentation"
```

### HTML 생성

```bash
./scripts/update-html.sh
```

### 확인

```bash
# 로컬 HTML 열기
open docs/html/index.html

# 통합 어드민에서 보기
# http://localhost:8100
```

---

## 디렉토리 구조

설치 후:

```
your-project/
├── docs/
│   ├── dev-log/              # 마크다운 (Git 커밋)
│   └── html/                 # HTML (선택적 커밋)
│       ├── index.html        # Kanban Board
│       ├── timeline.html     # 타임라인
│       └── data/dev-logs.json # 데이터
└── scripts/
    ├── dev-log.sh           # 로그 작성
    └── update-html.sh       # HTML 생성
```

---

## 여러 프로젝트 관리

```bash
# 프로젝트 A
cd ~/01_DEV/project-a/
~/dev-log-template/install-devlog.sh

# 프로젝트 B
cd ~/01_DEV/project-b/
~/dev-log-template/install-devlog.sh

# 통합 어드민에서 모두 확인
cd ~/dev-log-admin
python server.py
# http://localhost:8100
```

---

## 업데이트

```bash
cd your-project/
~/dev-log-template/update-devlog.sh
```

- 기존 데이터 보존
- 스크립트만 업데이트
- 자동 백업

---

## 문제 해결

### 템플릿이 없다면?

```bash
# 기존 프로젝트에서 생성
cd your-existing-project
cp -r scripts ~/dev-log-template/
cp docs/html/styles.css ~/dev-log-template/
cp docs/html/scripts.js ~/dev-log-template/
```

### 통합 어드민 없이 사용

각 프로젝트는 독립적으로 실행됩니다:

```bash
open docs/html/index.html
```

---

## 다음 단계

📖 [README.md](README.md) - 상세 문서
🔧 [설치 스크립트](install-devlog.sh)
🔄 [업데이트 스크립트](update-devlog.sh)

---

**Tip**: Git hook 설정하면 커밋마다 자동으로 dev-log 생성됩니다!
