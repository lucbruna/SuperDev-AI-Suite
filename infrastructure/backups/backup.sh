#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting backup..."

# Database backup
pg_dump -h "$DB_HOST" -U "$DB_USER" -d superdev | gzip > "$BACKUP_DIR/database.sql.gz"

# Redis backup
redis-cli -h "$REDIS_HOST" BGSAVE
sleep 5
cp /data/dump.rdb "$BACKUP_DIR/redis.rdb"

# Config backup
cp -r /app/config "$BACKUP_DIR/config"

echo "Backup completed: $BACKUP_DIR"
