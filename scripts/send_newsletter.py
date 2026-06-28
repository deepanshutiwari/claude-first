#!/usr/bin/env python3
"""
Claude Architect Exam Prep Newsletter
Generates and sends the daily newsletter using Claude API + Gmail SMTP.
"""

import json
import os
import smtplib
import sys
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent.parent
TOPICS_FILE = ROOT / "newsletters" / "topics.json"
TEMPLATE_FILE = ROOT / "newsletters" / "template.html"


def get_newsletter_number() -> int:
    start_date_str = os.environ.get("START_DATE")
    if not start_date_str:
        raise ValueError("START_DATE environment variable not set (format: YYYY-MM-DD)")
    start = date.fromisoformat(start_date_str)
    today = date.today()
    delta = (today - start).days + 1
    if delta < 1 or delta > 10:
        print(f"Day {delta} — outside the 10-newsletter window. Nothing to send.")
        sys.exit(0)
    return delta


def generate_deep_dive(client: anthropic.Anthropic, topic: dict) -> str:
    subtopics_text = "\n".join(f"- {s}" for s in topic["subtopics"])
    prompt = f"""You are writing the deep-dive section of an engaging daily newsletter for someone preparing for the Claude Certified Architect exam.

Topic: {topic["title"]}
Subtopics to cover:
{subtopics_text}

Write a rich, engaging deep-dive (400-550 words) that:
1. Explains the core concepts clearly with concrete examples
2. Uses analogies where helpful
3. Highlights what an architect needs to DECIDE, not just know
4. Includes at least one code snippet or API example in <code> tags where relevant
5. Has a punchy, memorable closing line

Format as HTML paragraphs (<p> tags). Use <code> for inline code. Use <blockquote><p> for important callouts.
Do NOT include a heading. Just the content paragraphs.
Be direct, specific, and avoid fluff."""

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_opening_hook(client: anthropic.Anthropic, topic: dict, number: int) -> str:
    prompt = f"""Write a punchy 2-sentence opening hook for newsletter issue {number}/10 about "{topic["title"]}" for Claude Certified Architect exam prep.

Make it motivating, specific to today's topic, and slightly urgent.
Format as a single <p> tag."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def build_html(template: str, topic: dict, number: int, deep_dive: str, opening_hook: str, topics: list) -> str:
    topics_html = "\n".join(f"<li>{s}</li>" for s in topic["subtopics"])

    quiz_items = []
    for item in topic["quiz_questions"]:
        quiz_items.append(
            f'<div class="quiz-item">'
            f'<div class="quiz-q">Q: {item["q"]}</div>'
            f'<div class="quiz-a">A: {item["a"]}</div>'
            f"</div>"
        )
    quiz_html = "\n".join(quiz_items)

    progress_pct = int((number / 10) * 100)

    next_title = topics[number]["title"] if number < 10 else "You're done! Time to take the exam 🎉"
    next_emoji = topics[number]["emoji"] if number < 10 else "🏁"

    html = template
    html = html.replace("{{number}}", str(number))
    html = html.replace("{{emoji}}", topic["emoji"])
    html = html.replace("{{title}}", topic["title"])
    html = html.replace("{{tagline}}", topic["tagline"])
    html = html.replace("{{progress_pct}}", str(progress_pct))
    html = html.replace("{{opening_hook}}", opening_hook)
    html = html.replace("{{topics_html}}", topics_html)
    html = html.replace("{{deep_dive_html}}", deep_dive)
    html = html.replace("{{exam_gotcha}}", topic["exam_gotcha"])
    html = html.replace("{{key_concept}}", topic["key_concept"])
    html = html.replace("{{quiz_html}}", quiz_html)
    html = html.replace("{{next_title}}", f"{next_emoji} {next_title}")

    return html


def send_email(html: str, subject: str):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("RECIPIENT_EMAIL", gmail_user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Claude Architect Prep <{gmail_user}>"
    msg["To"] = recipient

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())

    print(f"✓ Newsletter sent to {recipient}")


def main():
    number = get_newsletter_number()
    print(f"Sending newsletter #{number}...")

    topics = json.loads(TOPICS_FILE.read_text())
    # topics is 0-indexed in the list but 1-indexed by number
    topic = topics[number - 1]
    template = TEMPLATE_FILE.read_text()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    print("Generating content with Claude...")
    opening_hook = generate_opening_hook(client, topic, number)
    deep_dive = generate_deep_dive(client, topic, number)

    html = build_html(template, topic, number, deep_dive, opening_hook, topics)

    subject = f"[Day {number}/10] {topic['emoji']} {topic['title']} · Claude Architect Prep"
    send_email(html, subject)
    print(f"✓ Done! Issue {number}/10 delivered.")


if __name__ == "__main__":
    main()
