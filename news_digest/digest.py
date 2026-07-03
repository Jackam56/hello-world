#!/usr/bin/env python3
"""Build and send a daily news digest, filtering out routine Trump coverage.

Configuration (sources, keywords) lives in config.py. Email credentials come
from environment variables so no secrets are stored in the repo:

    GMAIL_ADDRESS       Gmail account to send from
    GMAIL_APP_PASSWORD  Gmail App Password for that account
    DIGEST_TO_EMAIL     Address to send the digest to
"""

import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import format_datetime, parsedate_to_datetime

import feedparser

import config

USER_AGENT = "Mozilla/5.0 (compatible; DailyNewsDigest/1.0)"


def is_trump_related(title, summary):
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in config.TRUMP_KEYWORDS)


def is_severe_enough(title, summary):
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in config.TRUMP_SEVERITY_KEYWORDS)


def entry_is_recent(entry, cutoff):
    published = entry.get("published") or entry.get("updated")
    if not published:
        return True  # no date info: don't drop it
    try:
        dt = parsedate_to_datetime(published)
    except (TypeError, ValueError):
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt >= cutoff


def fetch_section(source_feeds, cutoff):
    """Fetch and filter entries for one section, tagging each with its source."""
    items = []
    for source_name, url in source_feeds:
        try:
            parsed = feedparser.parse(url, agent=USER_AGENT)
            if parsed.bozo and not parsed.entries:
                print(f"  [warn] {source_name}: could not parse feed ({parsed.bozo_exception})", file=sys.stderr)
                continue
        except Exception as exc:  # network errors, etc.
            print(f"  [warn] {source_name}: fetch failed ({exc})", file=sys.stderr)
            continue

        for entry in parsed.entries:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            link = entry.get("link", "")
            if not title or not link:
                continue
            if not entry_is_recent(entry, cutoff):
                continue
            if is_trump_related(title, summary) and not is_severe_enough(title, summary):
                continue
            items.append({"title": title, "link": link, "source": source_name})

    # de-dupe near-identical titles across sources within a section
    seen = set()
    deduped = []
    for item in items:
        key = item["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped[: config.MAX_ITEMS_PER_SECTION]


def build_digest():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.MAX_AGE_HOURS)
    sections = {}
    for section_name, feeds in config.FEEDS.items():
        print(f"Fetching section: {section_name}")
        sections[section_name] = fetch_section(feeds, cutoff)
    return sections


def render_html(sections, today):
    parts = [f"<h1>{config.EMAIL_SUBJECT_PREFIX} &ndash; {today}</h1>"]
    any_items = False
    for section_name, items in sections.items():
        parts.append(f"<h2>{section_name}</h2>")
        if not items:
            parts.append("<p><em>No stories today.</em></p>")
            continue
        any_items = True
        parts.append("<ul>")
        for item in items:
            parts.append(
                f'<li><a href="{item["link"]}">{item["title"]}</a> '
                f'<span style="color:#777;">&mdash; {item["source"]}</span></li>'
            )
        parts.append("</ul>")
    if not any_items:
        parts.append("<p>No stories cleared the filters today.</p>")
    return "\n".join(parts)


def render_text(sections, today):
    lines = [f"{config.EMAIL_SUBJECT_PREFIX} - {today}", ""]
    for section_name, items in sections.items():
        lines.append(section_name)
        lines.append("-" * len(section_name))
        if not items:
            lines.append("No stories today.")
        for item in items:
            lines.append(f"- {item['title']} ({item['source']})")
            lines.append(f"  {item['link']}")
        lines.append("")
    return "\n".join(lines)


def send_email(html_body, text_body, today):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    to_email = os.environ["DIGEST_TO_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{config.EMAIL_SUBJECT_PREFIX} - {today}"
    msg["From"] = gmail_address
    msg["To"] = to_email
    msg["Date"] = format_datetime(datetime.now(timezone.utc))

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_email], msg.as_string())


def main():
    today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    sections = build_digest()
    html_body = render_html(sections, today)
    text_body = render_text(sections, today)
    send_email(html_body, text_body, today)
    print("Digest sent.")


if __name__ == "__main__":
    main()
