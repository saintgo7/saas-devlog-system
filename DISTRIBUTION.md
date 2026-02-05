# Dev Log System - 배포 가이드

## 배포 패키지 생성

### 현재 구조

```
dev-log-system/
├── README.md              # 메인 문서
├── VERSION                # 버전 정보
├── install.sh             # 설치 스크립트
├── uninstall.sh           # 제거 스크립트
├── DISTRIBUTION.md        # 이 파일
├── template/              # 프로젝트 템플릿
├── admin/                 # 통합 어드민
├── claude-integration/    # Claude 통합
└── docs/                  # 문서
```

---

## 배포 방법

### Option 1: GitHub Release

1. GitHub 저장소 생성
2. 파일 푸시
3. Release 생성
4. 사용자 다운로드:
   ```bash
   git clone https://github.com/yourusername/dev-log-system.git
   cd dev-log-system
   ./install.sh
   ```

### Option 2: ZIP 파일

```bash
cd ~
tar -czf dev-log-system-v1.0.0.tar.gz dev-log-system/
```

사용자:
```bash
tar -xzf dev-log-system-v1.0.0.tar.gz
cd dev-log-system
./install.sh
```

### Option 3: 스크립트 다운로드

```bash
curl -fsSL https://your-domain.com/install.sh | bash
```

---

## 설치 테스트

### 깨끗한 환경에서 테스트

```bash
# 기존 설치 제거
./uninstall.sh

# 재설치
./install.sh

# 테스트
cd ~/test-project
~/dev-log-template/install-devlog.sh
./scripts/dev-log.sh "feat: test"
./scripts/update-html.sh
open docs/html/index.html
```

---

## 버전 관리

### VERSION 파일

`VERSION` 파일 형식: `MAJOR.MINOR.PATCH`

- **MAJOR**: 호환성 깨지는 변경
- **MINOR**: 기능 추가 (호환성 유지)
- **PATCH**: 버그 수정

### 변경 로그

`CHANGELOG.md` 작성:

```markdown
# Changelog

## [1.0.0] - 2026-02-05

### Added
- 초기 릴리스
- 8가지 시각화 페이지
- 통합 어드민
- Claude Code 통합
```

---

## 의존성

### 필수
- Python 3.8+
- Git

### 선택적
- FastAPI (통합 어드민)
- Uvicorn (통합 어드민)

---

## 플랫폼 지원

### macOS ✅
- 테스트 완료
- 기본 지원

### Linux ✅
- 호환 가능
- 테스트 필요

### Windows ⚠️
- WSL 필요
- Git Bash로 가능

---

## 배포 체크리스트

- [ ] README.md 업데이트
- [ ] VERSION 업데이트
- [ ] CHANGELOG.md 작성
- [ ] 모든 스크립트 실행 권한 확인
- [ ] 깨끗한 환경에서 설치 테스트
- [ ] 문서 링크 확인
- [ ] 라이선스 파일 추가
- [ ] .gitignore 설정
- [ ] GitHub 저장소 생성
- [ ] Release 태그 생성

---

## 사용자 설치 플로우

```
1. 패키지 다운로드
   ↓
2. ./install.sh 실행
   ↓
3. ~/dev-log-template/ 설치됨
4. ~/dev-log-admin/ 설치됨
5. ~/.claude/skills/dev-log/ 설치됨
   ↓
6. 프로젝트에 설치
   ~/dev-log-template/install-devlog.sh
   ↓
7. 사용
   ./scripts/dev-log.sh
   ./scripts/update-html.sh
```

---

## 업데이트 플로우

```
1. 새 버전 다운로드
   ↓
2. ./install.sh 실행
   ↓
3. 기존 config.json, devlog.db 자동 백업
   ↓
4. 파일 업데이트
   ↓
5. 백업 복원
   ↓
6. 각 프로젝트 업데이트
   ~/dev-log-template/update-devlog.sh
```

---

## 제거 플로우

```
1. ./uninstall.sh 실행
   ↓
2. 백업 생성 옵션
   ↓
3. ~/dev-log-template/ 제거
4. ~/dev-log-admin/ 제거
5. ~/.claude/skills/dev-log/ 제거
   ↓
6. 프로젝트 dev-logs는 유지
```

---

## 패키지 파일 목록

### 필수 파일
- README.md
- VERSION
- install.sh
- uninstall.sh
- template/ (전체)
- admin/ (전체)
- claude-integration/ (전체)
- docs/ (전체)

### 제외 파일
- .DS_Store
- __pycache__/
- *.pyc
- .git/
- devlog.db (개인 데이터)
- config.json (개인 설정)

---

## .gitignore 추천

```gitignore
# macOS
.DS_Store

# Python
__pycache__/
*.py[cod]
*$py.class

# Dev Log Admin
admin/devlog.db
admin/server.log

# 개인 설정
admin/config.json

# Backups
*-backup-*/
*.backup
```

---

## LICENSE

MIT License 권장:

```
MIT License

Copyright (c) 2026 Ph.D SNT Go.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 배포 URL

### GitHub
```
https://github.com/yourusername/dev-log-system
```

### 다운로드
```
https://github.com/yourusername/dev-log-system/releases/latest
```

### 설치
```bash
git clone https://github.com/yourusername/dev-log-system.git
cd dev-log-system
./install.sh
```

---

## 문의

- GitHub Issues
- Email: your@email.com
- Documentation: README.md

---

**Happy Distributing!** 🚀
