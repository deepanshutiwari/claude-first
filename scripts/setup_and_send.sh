#!/bin/bash
# One-time setup: enter credentials securely, send newsletter #1 immediately.
set -e
cd "$(dirname "$0")/.."

echo ""
echo "=== Claude Architect Newsletter Setup ==="
echo "Credentials are stored locally in .env (not in chat history)"
echo ""

read -p    "Gmail address       : " GMAIL_USER
read -s -p "Gmail App Password  : " GMAIL_APP_PASSWORD; echo ""
read -p    "Anthropic API key   : " ANTHROPIC_API_KEY
read -p    "Start date (YYYY-MM-DD, today for newsletter #1): " START_DATE

RECIPIENT_EMAIL="$GMAIL_USER"

# Write .env
cat > .env << ENVEOF
GMAIL_USER=$GMAIL_USER
GMAIL_APP_PASSWORD=$GMAIL_APP_PASSWORD
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
RECIPIENT_EMAIL=$RECIPIENT_EMAIL
START_DATE=$START_DATE
ENVEOF

echo ""
echo "Credentials saved to .env"
echo "Installing dependencies..."
pip install anthropic -q

echo "Sending newsletter..."
export $(grep -v '^#' .env | xargs)
python3 scripts/send_newsletter.py

echo ""
echo "Done! Newsletter sent."
echo ""
echo "For future sends, run: bash scripts/run_now.sh"
echo "Or keep this Claude Code session open — the daily cron fires at 10am EST."
