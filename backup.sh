#!/bin/bash
set -euo pipefail

BACKUP_DIR="/var/backups/trillium"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Database backup
python manage.py dumpdata --natural-foreign --natural-primary > "$BACKUP_DIR/trillium_backup_${DATE}.json"

# Media backup
cp -R media "$BACKUP_DIR/media_${DATE}"

echo "Backup completed at $BACKUP_DIR"
