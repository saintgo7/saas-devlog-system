<!-- 프로젝트 현황·검증 결과·잔여 작업을 기록하는 스윕 상태 문서 -->
# STATUS — saas-devlog-system

_최종 갱신: 2026-06-14 (자동 포트폴리오 스윕 / 브랜치 `claude/sweep-2026-06-13`)_

## 한국어 본문

### 목적
프로젝트별 개발 이력을 자동으로 추적·시각화하는 시스템이다. 각 프로젝트에 템플릿을 설치하면 개발 로그를 마크다운으로 남기고, Python 스크립트가 이를 8종 HTML 페이지(칸반·타임라인·히트맵·파일·커밋크기·시간분석·배포·통계)로 변환한다. 여러 프로젝트를 한곳에서 보는 FastAPI 기반 통합 어드민(`admin/`)과 Claude Code 스킬 연동(`claude-integration/`)을 함께 제공한다.

### 프로젝트 유형
설치형 도구 + 정적 사이트 생성기 + 로컬 FastAPI 어드민의 복합체다. 라이브러리가 아니라 셸/Python 스크립트 모음과 배포 패키지에 가깝다. "완성"의 기준은 (1) 설치 스크립트가 동작하고, (2) 생성 스크립트가 로그를 HTML로 변환하며, (3) 어드민 서버가 기동되어 다중 프로젝트를 보여주는 것이다.

### 현재 상태 (검증된 사실)
- **언어 구성**: Python 12개 파일, 셸 13개, 문서 12개(`.md`). 테스트 스위트는 없음(triage `has tests: false`와 일치).
- **Python 컴파일**: `admin/`의 4개 파일(`server.py` 879줄, `sync.py`, `database.py`, `auto-register.py`)과 `template/scripts/`의 9개 생성 스크립트 전부 `python3 -m py_compile` 통과. 검증 환경 Python 3.11.5.
- **셸 문법**: `install.sh`, `uninstall.sh`, `template/install-devlog.sh`, `template/update-devlog.sh`, `template/scripts/*.sh`, `admin/startup.sh`, `template/scripts/etc/*.sh` 모두 `bash -n` 통과.
- **어드민 서버 임포트**: `admin/` 디렉터리에서 `import server` 성공. FastAPI 0.115.0 설치 확인, 앱 객체 로드됨(`Dev Log Admin API 1.0.0`).
- **샘플 데이터**: `admin/sample-data/`의 project-a/b/c `dev-logs.json` 모두 유효한 JSON(각 15/3/10 엔트리).
- **설치 일관성**: `install.sh`는 `template/` 디렉터리 전체를 재귀 복사(`cp -r`)하므로, WIP에서 일부 스크립트를 `template/scripts/etc/`로 옮긴 것이 설치를 깨뜨리지 않는다. 설치 스크립트에 옮겨진 스크립트(`setup.sh`, `deploy.sh`, `init-db.sql` 등)를 직접 참조하는 끊어진 경로 없음.

### 동작하는 것 vs 미확인
- **동작 확인(정적 검증)**: 전체 Python 컴파일, 전체 셸 문법, 어드민 모듈 임포트, 샘플 JSON 파싱.
- **미실행(unverified)**: 어드민 서버 실제 기동(`uvicorn`/HTTP 응답), `install.sh` 엔드투엔드 설치, 생성 스크립트의 실제 HTML 산출, 브라우저에서의 8종 페이지 렌더링은 이번 스윕에서 시간 제약(120초)으로 실행하지 않았다. 정적 검증만 통과했으므로 런타임 정상 여부는 미확인이다.

### 미완(dirty WIP)의 정체
이 저장소는 49개의 미커밋 변경을 가진 상태로 들어왔다. 마지막 커밋(`930f5f1`)은 v1.0.0 릴리스 직후이고, 이후의 작업이 커밋되지 않은 채 쌓여 있었다. 주요 내용은 다음과 같다.
- **어드민 대폭 확장**: `server.py` +578줄, `static/styles.css` +1026줄, `static/app.js`·`search.js` 개편, 신규 프로젝트 상세 페이지(`static/project.html` + `project.js` 34KB)와 `favicon.svg` 추가.
- **신규 Python**: `admin/auto-register.py`(254줄, 프로젝트 자동 등록), `admin/startup.sh`.
- **스크립트 재구성**: 배포·백업·DB 계열 스크립트(`deploy.sh`, `deploy-ws.sh`, `backup.sh`, `restore.sh`, `rollback.sh`, `logs.sh`, `setup.sh`, `init-db.sql`, `seed-data.sql`, `migrations/`)를 `template/scripts/`에서 `template/scripts/etc/`로 이동(구위치 삭제, 신위치 추가).
- **시각화 스크린샷**: `dashboard-full.png`, `project-detail*.png` 3종 추가.
- **샘플 데이터·예시 docs**: `admin/sample-data/`, `template/docs/` 추가.
- **`.claude/settings.local.json`**: 로컬 권한 설정. 민감정보 아님.

이번 스윕은 이 WIP를 **그대로 체크포인트**했다. 코드 동작을 바꾸는 수정은 하지 않았다(전부 검증을 통과했고, 위험한 변경을 피하기 위해서다).

### 보안 점검
- `git ls-files`에 `.env`/`*.pem`/secret/credential/`*.key`/`*.crt`/`devlog.db`/`config.json` 등 추적 항목 **없음**.
- `firebase-debug.log`, `admin/devlog.db`, `admin/config.json`, `admin/logs/*.log`는 `.gitignore`(`*.log`, `admin/devlog.db`, `admin/config.json`)로 제외되어 `git add -A` 드라이런에서 스테이징 대상 아님(확인됨).

### 마무리까지 남은 구체 작업
1. **런타임 검증**: `cd admin && python3 server.py`로 기동 후 `http://localhost:8100` 응답·다중 프로젝트 표시 확인. (미실행)
2. **엔드투엔드 설치 테스트**: 임시 디렉터리에서 `./install.sh` → `~/dev-log-template/install-devlog.sh` → `dev-log.sh` → `update-html.sh` → HTML 산출까지 클린 환경 검증.
3. **README 동기화**: README의 패키지 구조 설명은 배포/DB 스크립트가 `template/scripts/` 직하에 있다고 적혀 있으나, WIP에서 `template/scripts/etc/`로 이동됨. 신규 `project.html`/`auto-register.py`/`startup.sh`도 README에 미기재. 구조 설명 갱신 필요.
4. **`DISTRIBUTION.md` 체크리스트의 `CHANGELOG.md`**: 아직 부재. v1.0.0 이후 변경분(어드민 확장·스크립트 재배치) 기록 필요.
5. **커밋 분할 권고**: WIP를 의미 단위(어드민 UI / 스크립트 재배치 / 샘플데이터·스크린샷)로 나눠 재커밋하면 되돌리기 단위가 명확해짐. 이번엔 안전 체크포인트 목적상 한 커밋으로 묶음.

## English Summary
**Purpose**: An installable system that auto-tracks and visualizes per-project dev history. Markdown dev logs → 9 Python generators → 8 static HTML pages, plus a FastAPI multi-project admin and a Claude Code skill.

**Type**: Installer + static-site generator + local FastAPI admin (not a library). "Finished" = installer works, generators emit HTML, admin serves multiple projects.

**Verified now (static checks only)**: All Python (`admin/` 4 files + 9 template generators) passes `py_compile` on Python 3.11.5. All shell scripts (incl. `template/scripts/etc/*.sh`) pass `bash -n`. `admin/server.py` imports cleanly with FastAPI 0.115.0. All three `sample-data` JSON files parse (15/3/10 entries). `install.sh` recursively copies `template/`, so the WIP move of scripts into `template/scripts/etc/` does not break install — no broken references found.

**NOT verified (time-boxed)**: live server startup / HTTP, end-to-end `install.sh`, actual HTML generation, browser rendering. Runtime correctness is unverified.

**Dirty WIP checkpointed (not modified)**: 49 uncommitted changes post-v1.0.0 — large admin expansion (`server.py` +578, `styles.css` +1026, new `project.html`/`project.js`), new `auto-register.py`/`startup.sh`, scripts reorganized into `etc/`, screenshots, sample data, `.claude` local settings. No code behavior changed this sweep.

**Security**: No secrets tracked; `firebase-debug.log`, `devlog.db`, `config.json`, and `*.log` are gitignored and confirmed not staged.

**Remaining to finish**: (1) runtime-verify admin server on :8100; (2) clean-env end-to-end install test; (3) sync README package-structure section with the `etc/` move and new files; (4) add `CHANGELOG.md` per `DISTRIBUTION.md`; (5) optionally split the WIP into semantic commits.

> No book/paper outline: this is a tooling/distribution project, not research or substantial documentation warranting a paper.
