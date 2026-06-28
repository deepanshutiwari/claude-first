#!/usr/bin/env python3
"""
Local test script — generates newsletter HTML without sending email.
Usage: START_DATE=2026-06-28 ANTHROPIC_API_KEY=sk-... python scripts/test_local.py [newsletter_number]
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

# Allow overriding newsletter number for testing
if len(sys.argv) > 1:
    os.environ["START_DATE"] = date.today().isoformat()
    target_number = int(sys.argv[1])
    # Patch get_newsletter_number to return target
    from datetime import timedelta
    override_start = date.today() - timedelta(days=target_number - 1)
    os.environ["START_DATE"] = override_start.isoformat()

sys.path.insert(0, str(Path(__file__).parent))

import anthropic
from send_newsletter import (
    TEMPLATE_FILE,
    TOPICS_FILE,
    build_html,
    generate_deep_dive,
    generate_opening_hook,
    get_newsletter_number,
)

number = get_newsletter_number()
topics = json.loads(TOPICS_FILE.read_text())
topic = topics[number - 1]
template = TEMPLATE_FILE.read_text()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

print(f"Generating newsletter #{number}: {topic['title']}...")
opening_hook = generate_opening_hook(client, topic, number)
deep_dive = generate_deep_dive(client, topic, number)

html = build_html(template, topic, number, deep_dive, opening_hook, topics)

out_path = Path(f"/tmp/newsletter_{number}.html")
out_path.write_text(html)
print(f"✓ Written to {out_path}")
print(f"  Open with: open {out_path}")
