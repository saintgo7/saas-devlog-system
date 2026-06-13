#!/bin/bash
#
# 롤백 스크립트 - Workstation Manager
# 사용법: ./rollback.sh [version]
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 변수
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"

log_info "=========================================="
log_info "Workstation Manager 롤백 시작"
log_info "Time: $(date)"
log_info "=========================================="

# 1. 이전 버전 확인
check_previous_version() {
    if [ -n "$1" ]; then
        TARGET_VERSION="$1"
        log_info "지정된 버전으로 롤백: $TARGET_VERSION"
    else
        # 배포 히스토리에서 이전 버전 찾기
        if [ -f "${PROJECT_DIR}/.deploy_history" ]; then
            TARGET_VERSION=$(tail -2 "${PROJECT_DIR}/.deploy_history" | head -1)
            log_info "마지막 배포 버전으로 롤백: $TARGET_VERSION"
        else
            log_error "배포 히스토리를 찾을 수 없습니다."
            exit 1
        fi
    fi
}

# 2. 이전 커밋으로 되돌리기
rollback_code() {
    log_info "이전 커밋으로 되돌리는 중..."

    # Git 히스토리에서 이전 커밋 가져오기
    PREVIOUS_COMMIT=$(git log --format="%H" -2 | tail -1)
    log_info "이전 커밋: $PREVIOUS_COMMIT"

    git checkout "$PREVIOUS_COMMIT" -- .

    log_success "코드 롤백 완료"
}

# 3. 서비스 재배포
redeploy_services() {
    log_info "서비스 재배포 중..."

    docker compose -f "$COMPOSE_FILE" down --remove-orphans
    docker compose -f "$COMPOSE_FILE" up -d --build

    log_info "서비스 시작 대기 중..."
    sleep 15
}

# 4. DB 롤백 (선택적)
rollback_database() {
    log_warning "데이터베이스 롤백이 필요한 경우 수동으로 진행하세요:"
    log_info "1. 백업 파일 확인: ls -la ${BACKUP_DIR}/db_*.sql"
    log_info "2. 롤백 실행: docker exec -i wm_postgres psql -U postgres workstation_manager < backup.sql"
}

# 5. 헬스체크
health_check() {
    log_info "헬스체크 중..."

    for i in {1..30}; do
        if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
            log_success "서비스 정상 작동 확인"
            return 0
        fi
        sleep 2
    done

    log_error "헬스체크 실패"
    return 1
}

# 6. 최종 상태
show_status() {
    log_info "=========================================="
    log_info "롤백 완료 상태"
    log_info "=========================================="
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    log_success "롤백이 완료되었습니다!"
}

# 메인 실행
main() {
    check_previous_version "$1"
    rollback_code
    redeploy_services

    if health_check; then
        show_status
        rollback_database
        exit 0
    else
        log_error "롤백 후 헬스체크 실패!"
        log_info "수동 점검이 필요합니다."
        docker compose -f "$COMPOSE_FILE" logs --tail=50
        exit 1
    fi
}

main "$@"
