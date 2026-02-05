#!/bin/bash
# Workstation Manager - View Logs Script

# Colors
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Detect compose file
if [ -f docker-compose.dev.yml ] && docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.dev.yml"
elif [ -f docker-compose.prod.yml ] && docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

echo "================================================"
echo "  View Service Logs"
echo "================================================"
echo ""
echo "Select service:"
echo "  1) All services"
echo "  2) Frontend"
echo "  3) Server (Backend)"
echo "  4) Database"
echo "  5) Redis"
echo "  6) Celery Worker"
echo "  7) Celery Beat"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        SERVICE=""
        print_info "Showing logs for all services..."
        ;;
    2)
        SERVICE="frontend"
        print_info "Showing logs for Frontend..."
        ;;
    3)
        SERVICE="server"
        print_info "Showing logs for Server..."
        ;;
    4)
        SERVICE="db"
        print_info "Showing logs for Database..."
        ;;
    5)
        SERVICE="redis"
        print_info "Showing logs for Redis..."
        ;;
    6)
        SERVICE="celery"
        print_info "Showing logs for Celery Worker..."
        ;;
    7)
        SERVICE="celery-beat"
        print_info "Showing logs for Celery Beat..."
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
docker-compose -f "$COMPOSE_FILE" logs -f --tail=100 $SERVICE
