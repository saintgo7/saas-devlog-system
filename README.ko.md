# Dev Log System

*Read this in other languages: [English](README.md), [한국어](README.ko.md)*

개발 로그 자동 생성 및 시각화 시스템

**Version**: 1.0
**Author**: Ph.D SNT Go.
**License**: MIT

---

## 🎯 개요

각 프로젝트의 개발 히스토리를 자동으로 추적하고 시각화하는 시스템입니다.

### 주요 기능

- ✅ **자동 로그 생성**: 간단한 명령어로 개발 로그 작성
- ✅ **8가지 시각화**: Kanban, Timeline, Heatmap, Files, Size, Time, Deployment, Stats
- ✅ **통합 관리**: 여러 프로젝트를 하나의 대시보드에서 관리
- ✅ **Claude Code 통합**: AI 보조로 자동 로그 작성
- ✅ **Git 통합**: 개발 히스토리와 함께 버전 관리
- ✅ **독립 실행**: 각 프로젝트 독립적으로 동작
- ✅ **SQLite 기반**: 가벼운 데이터베이스

---

## 🚀 빠른 시작

### 1. 시스템 설치 (1분)

```bash
git clone https://github.com/saintgo7/saas-devlog-system.git
cd saas-devlog-system
./install.sh
```

설치되는 것:
- `~/dev-log-template/` - 프로젝트 템플릿
- `~/dev-log-admin/` - 통합 어드민
- `~/.claude/skills/dev-log/` - Claude Code 스킬

### 2. 프로젝트에 설치 (1분)

```bash
cd your-project/
~/dev-log-template/install-devlog.sh
```

대화형으로 프로젝트 정보 입력.

### 3. 사용

```bash
# 개발 로그 작성
./scripts/dev-log.sh "feat: add new feature"

# HTML 생성
./scripts/update-html.sh

# 확인
open docs/html/index.html
```

---

## 📦 패키지 구조

```
dev-log-system/
├── README.md              # 이 파일
├── install.sh             # 마스터 설치 스크립트
├── template/              # 프로젝트별 템플릿
│   ├── scripts/           # Python 생성 스크립트 (9개)
│   ├── styles.css         # CSS
│   ├── scripts.js         # JavaScript
│   ├── install-devlog.sh  # 프로젝트 설치 스크립트
│   ├── update-devlog.sh   # 업데이트 스크립트
│   └── README.md          # 템플릿 문서
├── admin/                 # 통합 어드민
│   ├── server.py          # FastAPI 서버
│   ├── sync.py            # 동기화 스크립트
│   ├── database.py        # SQLite 초기화
│   ├── config.json        # 프로젝트 설정
│   ├── static/            # 프론트엔드
│   └── README.md          # 어드민 문서
├── claude-integration/    # Claude Code 통합
│   ├── SKILL.md           # 스킬 정의
│   └── CLAUDE-TEMPLATE.md # 프로젝트 CLAUDE.md 템플릿
└── docs/                  # 문서
    ├── QUICKSTART.md      # 빠른 시작 가이드
    └── ARCHITECTURE.md    # 아키텍처 분석
```

---

## 🎨 시각화 페이지

각 프로젝트에 8가지 HTML 페이지 생성:

1. **index.html** - Kanban Board
   - 타입별 필터링
   - 검색 기능
   - 북마크
   - 고급 검색

2. **timeline.html** - Timeline View
   - 시간순 정렬
   - 날짜별 그룹화
   - 상세 정보

3. **heatmap.html** - Activity Heatmap
   - 월별/일별 활동량
   - 색상 코딩
   - 패턴 분석

4. **files.html** - File Change History
   - 파일별 변경 추적
   - 카테고리별 분류
   - Hot files 분석

5. **commit-size.html** - Commit Size Analysis
   - 커밋 크기 분포
   - 베스트 프랙티스
   - 추천사항

6. **time-analysis.html** - Time-based Analysis
   - 시간대별 패턴
   - 요일별 분석
   - 생산성 인사이트

7. **deployment.html** - Deployment History
   - 배포 히스토리
   - CI/CD 분석
   - 빈도 추적

8. **stats.html** - Statistics Dashboard
   - 전체 통계
   - 타입별 분포
   - 트렌드 분석

---

## 🌐 통합 어드민

여러 프로젝트를 한눈에:

```bash
cd ~/dev-log-admin
python3 server.py
# http://localhost:8100
```

**기능:**
- 전체 프로젝트 대시보드
- 통합 검색
- 프로젝트 간 비교
- 실시간 동기화

---

## 🤖 Claude Code 통합

Claude Code가 자동으로:
- 작업 완료 감지
- Dev log 작성 제안
- HTML 생성
- Git 커밋 포함

**트리거 키워드:**
- "dev log 작성"
- "로그 남겨줘"
- "HTML 생성"
- "devlog 설치"

---

## 📖 시스템 워크플로우

### 개별 프로젝트

```
1. 코드 작성
2. 테스트
3. Git 커밋
4. ./scripts/dev-log.sh "type: description"
5. ./scripts/update-html.sh
6. open docs/html/index.html
```

### 통합 관리

```
여러 프로젝트 → dev-logs.json → SQLite → 통합 대시보드
```

### 아키텍처

```
project-a/docs/html/         # 독립 실행
project-b/docs/html/         # 독립 실행
project-c/docs/html/         # 독립 실행
        ↓
~/dev-log-admin/             # 통합 뷰 (선택적)
```

---

## 🔧 요구사항

### 필수
- Python 3.8+
- Git

### 선택 (통합 어드민)
- FastAPI
- Uvicorn

설치:
```bash
pip3 install fastapi uvicorn
```

---

## 📚 문서

- **빠른 시작**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **아키텍처**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **템플릿**: [template/README.md](template/README.md)
- **어드민**: [admin/README.md](admin/README.md)

---

## 🎯 사용 사례

### 1. 개인 프로젝트
각 프로젝트의 개발 히스토리 추적

### 2. 팀 협업
여러 프로젝트 통합 관리

### 3. 포트폴리오
개발 활동 시각화

### 4. 오픈소스
Git과 함께 히스토리 공유

### 5. 프리랜서
클라이언트에게 작업 내역 제공

---

## 🌟 주요 특징

### 독립성
- 각 프로젝트는 완전 독립
- Git clone만 해도 dev-log 포함
- 오프라인 동작

### 확장성
- 프로젝트 추가 간단
- 무제한 프로젝트
- SQLite로 가벼움

### 통합성
- Claude Code 자동화
- Git 통합
- 통합 어드민 제공

### 버전 관리
- Git으로 히스토리 추적
- 시간 여행 가능
- 브랜치별 독립

---

## 🔄 업데이트

### 템플릿 업데이트
```bash
cd your-project/
~/dev-log-template/update-devlog.sh
```

### 시스템 재설치
```bash
cd ~/saas-devlog-system
git pull
./install.sh
```

---

## 🐛 문제 해결

### "Template not found"
```bash
cd ~/saas-devlog-system
./install.sh
```

### "Python packages not found"
```bash
pip3 install fastapi uvicorn
```

### 데이터 손실
Git으로 복구:
```bash
git checkout HEAD~1 -- docs/html/data/dev-logs.json
```

---

## 📊 통계

- **코드량**: ~1,500줄
- **설치 시간**: 1분
- **프로젝트 추가**: 1분
- **지원 언어**: Python, Shell, JavaScript
- **지원 브라우저**: Modern browsers

---

## 🎓 배운 점

### 설계 원칙
1. **분산 > 중앙**: 각 프로젝트 독립성
2. **Git = 백업**: 별도 백업 불필요
3. **정적 HTML**: 빠르고 안정적
4. **SQLite**: 가벼운 통합

### 기술 스택
- Python: 데이터 처리
- JavaScript: 인터랙션
- CSS: 다크모드 테마
- SQLite: 통합 DB
- FastAPI: REST API

---

## 📝 라이선스

MIT License

Copyright (c) 2026 Ph.D SNT Go.

---

## 🤝 기여

이슈 및 PR 환영합니다!

---

## 📧 지원

- GitHub: https://github.com/saintgo7/saas-devlog-system
- Issues: https://github.com/saintgo7/saas-devlog-system/issues
- Releases: https://github.com/saintgo7/saas-devlog-system/releases
- Docs: https://github.com/saintgo7/saas-devlog-system/tree/main/docs

---

## 🎉 감사합니다!

Dev Log System으로 개발 히스토리를 체계적으로 관리하세요!

**Enjoy coding!** 🚀
