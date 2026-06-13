#!/bin/bash
# Workstation Manager - Database Restore Script

set -e

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"

DB_CONTAINER=${DB_CONTAINER:-"wm_postgres_prod"}
DB_NAME=${POSTGRES_DB:-"workstation_manager"}
DB_USER=${POSTGRES_USER:-"postgres"}

echo "================================================"
echo "  Database Restore Script"
echo "================================================"
echo ""

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    print_error "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# List available backups
print_info "Available backups:"
echo ""
backups=($(find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | sort -r))

if [ ${#backups[@]} -eq 0 ]; then
    print_error "No backup files found in $BACKUP_DIR"
    exit 1
fi

# Display backups with numbers
for i in "${!backups[@]}"; do
    filename=$(basename "${backups[$i]}")
    size=$(du -h "${backups[$i]}" | cut -f1)
    date=$(echo "$filename" | grep -oP '\d{8}_\d{6}')
    formatted_date=$(date -d "${date:0:8} ${date:9:2}:${date:11:2}:${date:13:2}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$date")

    printf "%2d) %s (%s) - %s\n" $((i+1)) "$filename" "$size" "$formatted_date"
done

echo ""
read -p "Select backup to restore [1-${#backups[@]}]: " selection

# Validate selection
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#backups[@]} ]; then
    print_error "Invalid selection"
    exit 1
fi

BACKUP_FILE="${backups[$((selection-1))]}"

print_info "Selected backup: $(basename "$BACKUP_FILE")"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    # Try development container
    DB_CONTAINER="wm_postgres_dev"
    if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
        print_error "No database container is running"
        exit 1
    fi
    print_info "Using development container: $DB_CONTAINER"
fi

# Warning
echo ""
print_warning "WARNING: This will OVERWRITE the current database!"
print_warning "All existing data will be LOST!"
echo ""
read -p "Are you sure you want to continue? Type 'yes' to confirm: " confirm

if [ "$confirm" != "yes" ]; then
    print_info "Restore cancelled"
    exit 0
fi

# Stop dependent services
print_info "Stopping dependent services..."
docker-compose -f docker-compose.*.yml stop server celery celery-beat 2>/dev/null || true

# Drop existing connections
print_info "Terminating existing database connections..."
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d postgres <<EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
EOF

# Drop and recreate database
print_info "Dropping and recreating database..."
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d postgres <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF

# Restore backup
print_info "Restoring backup..."
gunzip -c "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" "$DB_NAME"

if [ $? -eq 0 ]; then
    print_success "Database restored successfully"
else
    print_error "Restore failed"
    exit 1
fi

# Restart services
echo ""
read -p "Do you want to restart services now? [Y/n]: " restart

if [ "$restart" != "n" ] && [ "$restart" != "N" ]; then
    print_info "Restarting services..."
    docker-compose -f docker-compose.*.yml up -d 2>/dev/null || docker-compose up -d
    print_success "Services restarted"
fi

echo ""
print_success "Restore completed successfully"
echo ""
