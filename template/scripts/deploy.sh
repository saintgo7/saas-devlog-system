#!/bin/bash
#
# 배포 스크립트 - Workstation Manager
# 사용법: ./deploy.sh [version]
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 변수
VERSION=${1:-"latest"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

log_info "=========================================="
log_info "Workstation Manager 배포 시작"
log_info "Version: $VERSION"
log_info "Time: $(date)"
log_info "=========================================="

# 1. 현재 상태 백업
backup_current_state() {
    log_info "현재 상태 백업 중..."

    # Docker 이미지 태그 백업
    docker images --format "{{.Repository}}:{{.Tag}}" | grep "wm_" > "${BACKUP_DIR}/images_${TIMESTAMP}.txt" || true

    # 현재 버전 저장
    if [ -f "${PROJECT_DIR}/.current_version" ]; then
        cp "${PROJECT_DIR}/.current_version" "${BACKUP_DIR}/version_${TIMESTAMP}.txt"
    fi

    # 데이터베이스 백업 (선택적)
    if docker ps --format '{{.Names}}' | grep -q "wm_postgres"; then
        log_info "데이터베이스 백업 중..."
        docker exec wm_postgres pg_dump -U postgres workstation_manager > "${BACKUP_DIR}/db_${TIMESTAMP}.sql" 2>/dev/null || log_warning "DB 백업 실패 (서비스 미실행)"
    fi

    log_success "백업 완료: ${BACKUP_DIR}"
}

# 2. 서비스 상태 확인
check_services() {
    log_info "현재 서비스 상태 확인..."
    docker compose -f "$COMPOSE_FILE" ps || true
}

# 3. 새 이미지 풀
pull_images() {
    log_info "Docker 이미지 업데이트 중..."
    docker compose -f "$COMPOSE_FILE" pull --ignore-pull-failures || true
}

# 4. 서비스 업데이트 (무중단)
update_services() {
    log_info "서비스 업데이트 중 (무중단 배포)..."

    # Backend 먼저 업데이트
    log_info "Backend 서비스 업데이트..."
    docker compose -f "$COMPOSE_FILE" up -d --no-deps --build server

    # Backend 헬스체크 대기
    log_info "Backend 헬스체크 대기 중..."
    sleep 10

    for i in {1..30}; do
        if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Backend 정상 작동 확인"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Backend 헬스체크 실패"
            return 1
        fi
        sleep 2
    done

    # Celery 업데이트
    log_info "Celery 워커 업데이트..."
    docker compose -f "$COMPOSE_FILE" up -d --no-deps --build celery || true

    # Frontend 업데이트
    log_info "Frontend 서비스 업데이트..."
    docker compose -f "$COMPOSE_FILE" up -d --no-deps --build frontend

    # Nginx 재시작 (설정 리로드)
    log_info "Nginx 재시작..."
    docker compose -f "$COMPOSE_FILE" restart nginx || true
}

# 5. 헬스체크
health_check() {
    log_info "전체 서비스 헬스체크..."

    local all_healthy=true

    # Backend 체크
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend: 정상"
    else
        log_error "Backend: 비정상"
        all_healthy=false
    fi

    # Frontend 체크
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend: 정상"
    else
        log_warning "Frontend: 응답 없음 (Nginx 통해 접근 가능)"
    fi

    # Nginx 체크 (메인 포트)
    if curl -sf http://localhost:9999/health > /dev/null 2>&1; then
        log_success "Nginx: 정상"
    else
        log_warning "Nginx: 응답 확인 필요"
    fi

    if [ "$all_healthy" = false ]; then
        return 1
    fi

    return 0
}

# 6. 정리
cleanup() {
    log_info "정리 작업 중..."

    # 미사용 이미지 정리
    docker image prune -f > /dev/null 2>&1 || true

    # 오래된 백업 삭제 (7일 이상)
    find "$BACKUP_DIR" -type f -mtime +7 -delete 2>/dev/null || true

    # 현재 버전 저장
    echo "$VERSION" > "${PROJECT_DIR}/.current_version"
    echo "$TIMESTAMP" >> "${PROJECT_DIR}/.deploy_history"
}

# 7. 최종 상태 출력
show_status() {
    log_info "=========================================="
    log_info "배포 완료 상태"
    log_info "=========================================="
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    log_success "배포가 완료되었습니다!"
    log_info "Version: $VERSION"
    log_info "Access URL: http://localhost:9999"
}

# 메인 실행
main() {
    backup_current_state
    check_services
    pull_images
    update_services

    if health_check; then
        cleanup
        show_status
        exit 0
    else
        log_error "헬스체크 실패! 롤백이 필요할 수 있습니다."
        log_info "롤백 명령: ./scripts/rollback.sh"
        exit 1
    fi
}

# 스크립트 실행
main "$@"
