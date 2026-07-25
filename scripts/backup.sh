#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="${DB_NAME:-superdev}"
DB_USER="${DB_USER:-superdev}"
S3_BUCKET="${S3_BUCKET:-}"

mkdir -p "$BACKUP_DIR"

pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

if [ -n "$S3_BUCKET" ]; then
  aws s3 cp "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" "s3://$S3_BUCKET/backups/"
fi

echo "Backup completed: $BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
