#!/bin/bash
# ============================================
# ws.abada.co.kr 배포 스크립트
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOMAIN="ws.abada.co.kr"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} ws.abada.co.kr 배포 스크립트${NC}"
echo -e "${GREEN}============================================${NC}"

# 1. 환경 파일 확인
echo -e "\n${YELLOW}[1/7] 환경 파일 확인...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}오류: .env 파일이 없습니다.${NC}"
    echo "cp .env.example .env 로 복사 후 수정하세요."
    exit 1
fi

# 보안 키 확인
if grep -q "change-this" "$PROJECT_DIR/.env"; then
    echo -e "${RED}경고: .env 파일의 보안 키를 변경하세요!${NC}"
    echo "SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY, AGENT_API_KEY"
    exit 1
fi

echo -e "${GREEN}✓ 환경 파일 확인 완료${NC}"

# 2. PostgreSQL 데이터베이스 생성
echo -e "\n${YELLOW}[2/7] PostgreSQL 데이터베이스 확인...${NC}"
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='workstation_manager'" 2>/dev/null || echo "")
if [ "$DB_EXISTS" != "1" ]; then
    echo "데이터베이스 생성 중..."
    sudo -u postgres psql -c "CREATE DATABASE workstation_manager;"
    echo -e "${GREEN}✓ 데이터베이스 생성 완료${NC}"
else
    echo -e "${GREEN}✓ 데이터베이스 이미 존재${NC}"
fi

# 3. Docker 이미지 빌드
echo -e "\n${YELLOW}[3/7] Docker 이미지 빌드...${NC}"
cd "$PROJECT_DIR"
docker compose -f docker-compose.ws.yml build --no-cache
echo -e "${GREEN}✓ Docker 이미지 빌드 완료${NC}"

# 4. Docker 컨테이너 시작
echo -e "\n${YELLOW}[4/7] Docker 컨테이너 시작...${NC}"
docker compose -f docker-compose.ws.yml up -d
echo -e "${GREEN}✓ Docker 컨테이너 시작 완료${NC}"

# 5. 헬스체크 대기
echo -e "\n${YELLOW}[5/7] 서비스 헬스체크 대기...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 백엔드 서비스 정상${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "대기 중... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}경고: 백엔드 서비스 응답 없음${NC}"
    echo "docker compose -f docker-compose.ws.yml logs server 로 로그 확인"
fi

# 6. SSL 인증서 발급 (이미 있으면 건너뜀)
echo -e "\n${YELLOW}[6/7] SSL 인증서 확인...${NC}"
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${GREEN}✓ SSL 인증서 이미 존재${NC}"
else
    echo "SSL 인증서 발급 중... (수동 실행 필요)"
    echo ""
    echo "다음 명령어를 실행하세요:"
    echo -e "${YELLOW}sudo certbot certonly --nginx -d $DOMAIN${NC}"
fi

# 7. Nginx 설정 활성화
echo -e "\n${YELLOW}[7/7] Nginx 설정 활성화...${NC}"
if [ ! -f "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    sudo cp "$PROJECT_DIR/nginx/ws.abada.co.kr.conf" "/etc/nginx/sites-available/$DOMAIN"
    sudo ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"
    sudo nginx -t && sudo systemctl reload nginx
    echo -e "${GREEN}✓ Nginx 설정 활성화 완료${NC}"
else
    echo -e "${GREEN}✓ Nginx 설정 이미 활성화됨${NC}"
fi

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN} 배포 완료!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "접속 URL: https://$DOMAIN"
echo "API 문서: https://$DOMAIN/docs"
echo ""
echo "컨테이너 상태 확인:"
echo "  docker compose -f docker-compose.ws.yml ps"
echo ""
echo "로그 확인:"
echo "  docker compose -f docker-compose.ws.yml logs -f"
