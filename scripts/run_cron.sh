#!/bin/bash
# Wrapper for cron — loads .env and runs the newsletter script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

set -a
source "$PROJECT_DIR/.env"
set +a

cd "$PROJECT_DIR"
/usr/bin/python3 scripts/send_newsletter.py >> "$PROJECT_DIR/newsletter.log" 2>&1
