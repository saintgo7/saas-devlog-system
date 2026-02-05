# Scripts Directory

Utility scripts for Workstation Manager operations.

## Available Scripts

### 🚀 setup.sh
Initial setup and installation script.

**Usage:**
```bash
./scripts/setup.sh
```

**Features:**
- Environment file creation
- Secret key generation
- SSL certificate generation (dev)
- Docker image building
- Service startup

**Interactive:**
- Environment selection (dev/prod)
- Service startup confirmation

---

### 💾 backup.sh
Database backup script.

**Usage:**
```bash
./scripts/backup.sh

# With custom retention
RETENTION_DAYS=60 ./scripts/backup.sh

# With custom container
DB_CONTAINER=custom_postgres ./scripts/backup.sh
```

**Features:**
- PostgreSQL dump
- Gzip compression
- Automatic cleanup (30 day retention)
- Timestamp-based naming

**Output:**
```
backups/backup_20240101_120000.sql.gz
```

**Automation:**
```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * cd /path/to/PRJ && ./scripts/backup.sh >> logs/backup.log 2>&1
```

---

### 🔄 restore.sh
Database restore script.

**Usage:**
```bash
./scripts/restore.sh
```

**Features:**
- Interactive backup selection
- Database recreation
- Connection termination
- Service management

**⚠️ Warning:** This will overwrite the current database!

---

### 📋 logs.sh
Interactive log viewer.

**Usage:**
```bash
./scripts/logs.sh
```

**Features:**
- Service selection menu
- Follow mode (real-time)
- Last 100 lines display
- Auto-detect compose file

**Services:**
1. All services
2. Frontend
3. Server (Backend)
4. Database
5. Redis
6. Celery Worker
7. Celery Beat

---

## Script Permissions

All scripts should be executable:

```bash
chmod +x scripts/*.sh
```

## Environment Variables

Scripts respect these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_CONTAINER` | `wm_postgres_prod` | PostgreSQL container name |
| `POSTGRES_USER` | `postgres` | Database username |
| `POSTGRES_DB` | `workstation_manager` | Database name |
| `RETENTION_DAYS` | `30` | Backup retention period |

## Error Handling

All scripts use `set -e` to exit on errors and provide colored output:
- 🔵 **INFO**: Informational messages
- 🟢 **SUCCESS**: Successful operations
- 🟡 **WARNING**: Warning messages
- 🔴 **ERROR**: Error messages

## Examples

### Complete Workflow

```bash
# 1. Initial setup
./scripts/setup.sh

# 2. View logs
./scripts/logs.sh

# 3. Create backup
./scripts/backup.sh

# 4. Restore from backup (if needed)
./scripts/restore.sh
```

### Scheduled Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /home/user/PRJ && ./scripts/backup.sh >> logs/backup.log 2>&1

# Add weekly cleanup at Sunday 3 AM
0 3 * * 0 find /home/user/PRJ/backups -name "*.sql.gz" -mtime +30 -delete
```

### Custom Backup Location

```bash
# Modify backup.sh
BACKUP_DIR="/mnt/backups/workstation-manager"
```

## Troubleshooting

### Script Not Executable
```bash
chmod +x scripts/script_name.sh
```

### Container Not Found
```bash
# List running containers
docker ps

# Specify custom container
DB_CONTAINER=custom_name ./scripts/backup.sh
```

### Permission Denied (Backup)
```bash
# Create backup directory with permissions
mkdir -p backups
chmod 755 backups
```

### Database Connection Failed
```bash
# Check container is running
docker ps | grep postgres

# Check database is ready
docker exec wm_postgres_dev pg_isready -U postgres
```

## Advanced Usage

### Backup to Remote Server

```bash
# Add to backup.sh
scp "$BACKUP_COMPRESSED" user@remote:/backups/
```

### Backup Rotation

```bash
# Keep only last 7 backups
ls -t backups/*.sql.gz | tail -n +8 | xargs rm -f
```

### Encrypted Backups

```bash
# Encrypt backup
gpg --encrypt --recipient your@email.com backup.sql.gz

# Decrypt
gpg --decrypt backup.sql.gz.gpg > backup.sql.gz
```

## Security Notes

1. **Backup Files**: Contains sensitive data, secure appropriately
2. **Credentials**: Never hardcode credentials in scripts
3. **Remote Backups**: Use encrypted transfer (SCP/SFTP)
4. **File Permissions**: Restrict access to backup files
5. **Restore Confirmation**: Always verify before restore

## Support

For issues with scripts:
1. Check script has execute permissions
2. Verify Docker containers are running
3. Check environment variables
4. Review script output for errors
5. Consult main documentation
