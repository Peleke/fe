"""Publish a composed briefing to Beehiiv and/or Telegram."""

import os
import json
from urllib.request import urlopen, Request


def publish_beehiiv(subject: str, body_html: str) -> dict:
    """Push a briefing to Beehiiv as a draft or published post.

    Args:
        subject: Email subject line.
        body_html: Full HTML body of the newsletter.

    Returns:
        Beehiiv API response dict.
    """
    api_key = os.environ["BEEHIIV_API_KEY"]
    pub_id = os.environ["BEEHIIV_PUBLICATION_ID"]
    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/posts"

    payload = json.dumps({
        "title": subject,
        "subtitle": "",
        "content": body_html,
        "status": "draft",  # Change to "published" for auto-send
    }).encode()

    req = Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def send_telegram(chat_id: str, text: str) -> dict:
    """Send a briefing to a Telegram chat via the bot API.

    Args:
        chat_id: Telegram chat/user ID.
        text: Plain text message (Markdown supported).

    Returns:
        Telegram API response dict.
    """
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode()

    req = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def text_to_html(text: str) -> str:
    """Convert plain-text briefing to minimal HTML for Beehiiv.

    Converts ᚠ headers to <h3>, blank lines to <br>, etc.
    """
    lines = text.split("\n")
    html_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("ᚠ "):
            heading = stripped[2:]
            html_lines.append(f"<h3 style='color:#6ee7b7;'>{heading}</h3>")
        elif stripped.startswith("• "):
            html_lines.append(f"<p style='margin:4px 0;'>{stripped}</p>")
        elif stripped == "":
            html_lines.append("<br>")
        elif stripped == "— ᚠ Fe":
            html_lines.append("<p style='color:#6ee7b7; margin-top:24px;'>— ᚠ Fe</p>")
        else:
            html_lines.append(f"<p>{stripped}</p>")

    return "\n".join(html_lines)
