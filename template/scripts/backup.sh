#!/bin/bash
# Workstation Manager - Database Backup Script

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Database configuration
DB_CONTAINER=${DB_CONTAINER:-"wm_postgres_prod"}
DB_NAME=${POSTGRES_DB:-"workstation_manager"}
DB_USER=${POSTGRES_USER:-"postgres"}

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "================================================"
echo "  Database Backup Script"
echo "================================================"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    print_error "Database container '$DB_CONTAINER' is not running"

    # Try development container
    DB_CONTAINER="wm_postgres_dev"
    if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
        print_error "No database container is running"
        exit 1
    fi

    print_info "Using development container: $DB_CONTAINER"
fi

# Backup filename
BACKUP_FILE="$BACKUP_DIR/backup_${DATE}.sql"
BACKUP_COMPRESSED="$BACKUP_FILE.gz"

print_info "Starting backup..."
print_info "Container: $DB_CONTAINER"
print_info "Database: $DB_NAME"
print_info "Output: $BACKUP_COMPRESSED"

# Perform backup
docker exec -t "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compress backup
    gzip "$BACKUP_FILE"

    # Get file size
    SIZE=$(du -h "$BACKUP_COMPRESSED" | cut -f1)

    print_success "Backup completed successfully"
    print_info "File: $BACKUP_COMPRESSED"
    print_info "Size: $SIZE"
else
    print_error "Backup failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Clean old backups
print_info "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

REMAINING=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | wc -l)
print_success "Cleanup complete. $REMAINING backup(s) remaining"

echo ""
print_success "All operations completed successfully"
echo ""
echo "To restore from this backup:"
echo "  gunzip -c $BACKUP_COMPRESSED | docker exec -i $DB_CONTAINER psql -U $DB_USER $DB_NAME"
echo ""
