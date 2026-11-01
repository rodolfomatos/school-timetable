#!/usr/bin/env bash
# restore.sh - Restore PostgreSQL database for school-timetable
# Usage: ./restore.sh <backup_file> [target_db_name]

set -euo pipefail

# Config
DB_NAME="${POSTGRES_DB:-school_timetable}"
DB_USER="${POSTGRES_USER:-school}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

# Parse arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_file> [target_db_name]"
    echo "Example: $0 backup_20240115_120000.sql.gz"
    echo "         $0 backup_20240115_120000.sql.gz school_timetable_restored"
    exit 1
fi

BACKUP_FILE="$1"
TARGET_DB="${2:-${POSTGRES_DB:-school_timetable}}"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "Restoring ${BACKUP_FILE} to database ${TARGET_DB}..."

# Check if target database exists, if not create it
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${TARGET_DB}'" | grep -q 1 || {
    echo "Creating database ${TARGET_DB}..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${TARGET_DB};"
}

# Check if it's a compressed custom format or plain SQL
if file "${BACKUP_FILE}" | grep -q "gzip compressed data"; then
    echo "Detected gzip compressed custom format backup..."
    pg_restore \
        --host="${DB_HOST}" \
        --port="${DB_PORT}" \
        --username="${DB_USER}" \
        --dbname="${TARGET_DB}" \
        --clean \
        --if-exists \
        --no-owner \
        --no-privileges \
        --jobs=4 \
        "${BACKUP_FILE}"
else
    echo "Detected plain SQL backup..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TARGET_DB}" -f "${BACKUP_FILE}"
fi

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo "✅ Restore completed successfully to ${TARGET_DB}"
else
    echo "❌ Restore failed!"
    exit 1
fi