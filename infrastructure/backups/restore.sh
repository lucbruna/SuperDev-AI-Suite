#!/bin/bash
set -euo pipefail

BACKUP_DIR="${1:?Usage: restore.sh <backup_dir>}"

if [ ! -d "$BACKUP_DIR" ]; then
  echo "Backup directory not found: $BACKUP_DIR"
  exit 1
fi

echo "Restoring from: $BACKUP_DIR"

# Restore database
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
  echo "Restoring database..."
  gunzip -c "$BACKUP_DIR/database.sql.gz" | psql -h "$DB_HOST" -U "$DB_USER" -d superdev
fi

# Restore Redis
if [ -f "$BACKUP_DIR/redis.rdb" ]; then
  echo "Restoring Redis..."
  cp "$BACKUP_DIR/redis.rdb" /data/dump.rdb
  redis-cli -h "$REDIS_HOST" SHUTDOWN NOSAVE
fi

echo "Restore completed"
