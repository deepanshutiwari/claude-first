#!/bin/bash
# Run today's newsletter immediately.
# Usage: bash scripts/run_now.sh
set -e
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "ERROR: .env file not found. Copy .env.template to .env and fill in your credentials."
  exit 1
fi

export $(grep -v '^#' .env | xargs)
pip install anthropic -q
python3 scripts/send_newsletter.py
