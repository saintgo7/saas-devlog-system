# STATUS — saas-devlog-system

> 자동 포트폴리오 스윕(claude/sweep-2026-06-13)으로 작성. 검증된 사실만 기록하고, 미검증 항목은 명시했다.

## 목적 (Purpose)

프로젝트별 개발 이력을 자동으로 추적·시각화하는 도구 모음이다.
개발 로그(마크다운)를 파싱해 8종의 정적 HTML 대시보드(칸반·타임라인·히트맵·파일 변경·커밋 크기·시간 분석·배포·통계)를 생성하고, 여러 프로젝트를 FastAPI + SQLite 기반 통합 관리자에서 한눈에 본다.
타입: CLI/툴링 + 정적 사이트 생성기 + 소규모 API 서버. 테스트 스위트는 없다.

## 현재 상태 (Current State)

이 저장소는 v1.0.0 릴리스 이후 v2.0.0(인프라 관리 기능) 작업이 진행 중인 더티 상태였다.
스윕 시점에 추적 중 수정 6개 + 미추적 다수가 워킹트리에 있었고, 이번 커밋에서 체크포인트로 함께 담았다.

### v2.0.0 변경 요지 (기존 WIP, 의도된 기능 증분으로 판단)

- `admin/database.py`: `servers`, `deployments`, `cloudflare_tunnels` 테이블 추가 + `migrate_db()`(projects에 domain/local_path/status 컬럼 안전 추가).
- `admin/server.py`: 인프라 API 6종 추가(`/api/servers`, `/api/servers/{slug}`, `/api/deployments`, `/api/projects/{slug}/deployments`, `/api/tunnels`, `/api/stats/infrastructure`). 버전 문자열 `2.0.0`.
- `admin/sync.py`: `sync_servers`, `sync_deployments`, `sync_cloudflare_tunnels` 추가. JSON 부재 프로젝트도 메타데이터만으로 동기화하도록 개선.
- `admin/static/`: `infrastructure.html`, `deployments.html`, `app.js`/`index.html` 수정(루트 StaticFiles 마운트로 자동 서빙).
- 신규 운영 스크립트: `admin/migrate.py`(프로젝트 디렉터리 도메인 이전), `admin/scan-inventory.py`(SSH/Cloudflare/디렉터리 스캔으로 config.json 자동 갱신).

## 동작하는 것 vs 안 되는 것 (Verified)

검증 근거는 이번 스윕에서 실제로 실행한 명령이다.

- 동작 — 전체 HTML 생성 파이프라인: `bash scripts/update-html.sh` 가 exit 0으로 완료. 파싱 2개 로그 → 8종 HTML 모두 생성 성공.
- 동작 — Python 컴파일: `py_compile` 22개 파일 전부 OK.
- 동작 — Shell 문법: `bash -n` 15개 스크립트 전부 OK.
- 동작 — DB 초기화/마이그레이션: 임시 DB에서 `init_db()`+`migrate_db()` 실행 시 `servers/deployments/cloudflare_tunnels` 테이블 및 projects의 domain/local_path/status 컬럼 생성 확인.
- 동작 — 서버 임포트: `admin/` 디렉터리에서 `import server` 성공, 라우트 19개(인프라 6종 포함). FastAPI 0.115.0, uvicorn 설치됨.
- 미검증 — 라이브 서버 엔드포인트 응답: `uvicorn.run`은 실행하지 않았다(외부 바인딩 회피). 임포트·라우트 등록까지만 확인.
- 미검증 — `migrate.py` / `scan-inventory.py` 실제 실행: 사용자의 실제 파일시스템(`~/01_DEV`)과 `~/.ssh/config`를 읽거나 파일을 이동하므로 안전상 실행하지 않았다. `py_compile`만 통과.
- 주의 — 테스트 스위트 없음: 회귀를 잡아낼 자동 테스트가 없어 검증은 "실행되는가" 수준에 머문다.

## 안전·리스크 메모 (Risk Notes)

- `admin/config.json`은 `.gitignore`에 등록되어 추적되지 않는다. 로컬 config에는 27개 프로젝트 + servers + cloudflare_tunnels 항목이 들어 있다(개인 인프라 정보). 커밋하지 않았다.
- `admin/migrate.py`는 `shutil`로 프로젝트 디렉터리를 실제 이동하고 심볼릭 링크를 정리하는 파괴적 동작을 포함한다. `--dry-run`/`--status`/`--audit` 외 옵션은 신중히 다뤄야 한다.
- 비밀정보 스캔에서 매칭된 `template/scripts/setup.sh`(placeholder 치환용 `your-secret-key-change-...`)와 `claude-integration/SKILL.md`(예시 커밋 메시지)는 실제 비밀이 아니다.
- 서버는 `directory="static"` 상대경로를 쓰므로 `admin/` 디렉터리에서 실행해야 한다(README 안내와 일치, 버그 아님).

## 이번 스윕에서 변경한 것 (Changes by this sweep)

- 추가: `STATUS.md`(본 파일).
- 추가: `admin/requirements.txt`(README가 `pip3 install fastapi uvicorn`를 안내하나 의존성 파일이 없었음 — 명백히 의도된 보완).
- 위 두 파일 외 코드 로직은 변경하지 않았다. 기존 WIP는 체크포인트로 함께 커밋했다.

## 완성까지 남은 작업 (Remaining Steps)

1. 라이브 통합 테스트: `cd admin && python3 server.py` 실행 후 6종 인프라 엔드포인트 응답·`infrastructure.html`/`deployments.html` 렌더 확인.
2. `scan-inventory.py` → `sync.py` 왕복 검증(스테이징/임시 config로 안전하게).
3. 최소 테스트 추가: `parse-devlog.py` 파싱과 `database.migrate_db()` 멱등성에 대한 pytest 스모크 테스트.
4. `admin/README.md`의 버전·신규 API 문서를 v2.0.0에 맞게 갱신.
5. 루트 README의 "Code Size ~1,500 lines" 등 통계 수치 재확인(인프라 기능 추가로 증가했을 가능성, 미검증).

## 책/논문 가능성 (Book/Paper Potential)

낮음. 연구 산출물이 아니라 개인 생산성 도구다. 다만 "분산형 vs 중앙형 개발 로그 관리", "Git=백업 원칙", "정적 HTML 시각화 + 경량 SQLite 통합" 같은 설계 원칙은 블로그/기술 노트 소재는 된다.

---

## English Summary

A tooling repo that turns markdown dev-logs into 8 static HTML dashboards and aggregates multiple projects in a FastAPI + SQLite admin. No test suite.

State: a v1.0.0 release with in-progress v2.0.0 work (infrastructure tracking: servers/deployments/Cloudflare tunnels). The pre-existing dirty WIP was checkpointed in this sweep commit.

Verified working (commands actually run this sweep): full `scripts/update-html.sh` pipeline exits 0 and generates all 8 HTML pages; `py_compile` passes for all 22 Python files; `bash -n` passes for all 15 shell scripts; `init_db()`+`migrate_db()` create the new tables/columns in a temp DB; `server.py` imports with 19 routes (6 new infra endpoints); FastAPI 0.115.0 present.

Not verified (intentionally, for safety): live server endpoint responses (did not bind a port); `migrate.py`/`scan-inventory.py` execution (they touch the user's real filesystem and `~/.ssh/config`).

This sweep added only `STATUS.md` and `admin/requirements.txt` (README references `pip3 install fastapi uvicorn` but no deps file existed). No code logic changed. `admin/config.json` holds personal infra data and is gitignored — not committed.

Remaining to "finish": live integration test of the v2 infra APIs and HTML pages; safe round-trip test of scan-inventory→sync; add minimal pytest smoke tests; refresh `admin/README.md` for v2.0.0.
