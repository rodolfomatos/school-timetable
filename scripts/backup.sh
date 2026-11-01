#!/usr/bin/env bash
# backup.sh - Backup PostgreSQL database for school-timetable
# Usage: ./backup.sh [output_file]
# If output_file not provided, uses: backup_YYYYMMDD_HHMMSS.sql.gz

set -euo pipefail

# Config
DB_NAME="${POSTGRES_DB:-school_timetable}"
DB_USER="${POSTGRES_USER:-school}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Output file
if [ $# -eq 1 ]; then
    OUTPUT_FILE="$1"
else
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"
fi

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

echo "Starting backup of ${DB_NAME} to ${OUTPUT_FILE}..."

# Run pg_dump with compression
pg_dump \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --dbname="${DB_NAME}" \
    --format=custom \
    --compress=9 \
    --no-owner \
    --no-privileges \
    --file="${OUTPUT_FILE}"

# Check if backup was successful
if [ $? -eq 0 ] && [ -f "${OUTPUT_FILE}" ]; then
    SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)
    echo "✅ Backup completed successfully: ${OUTPUT_FILE} (${SIZE})"
    
    # Cleanup old backups
    echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
    find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
    echo "Cleanup complete."
else
    echo "❌ Backup failed!"
    exit 1
fi