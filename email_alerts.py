import imaplib
import email as email_lib
import re
import smtplib
import ssl
import json
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr

import requests
from bs4 import BeautifulSoup
from decouple import config

EMAIL_ADDRESS = config("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = config("EMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = "unguryan77@gmail.com"
DIGEST_SUBJECT = "Your Weekly Tech Deals Digest"
DATA_FILE = "data.json"
WEEKLY_INTERVAL = timedelta(days=7)


def _load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def log_deal(title, place, price):
    data = _load_data()
    data.setdefault("dealsLog", []).append({
        "title": title,
        "place": place,
        "price": price,
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save_data(data)


def _send_email(subject, plain_body, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())


def _build_digest_html(deals):
    if deals:
        rows = "".join(
            "<tr>"
            f"<td style='padding:8px;border-bottom:1px solid #ddd'>{d['title']}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #ddd'>{d['place']}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #ddd'>{d['price']}</td>"
            "</tr>"
            for d in deals
        )
        deals_html = (
            "<table style='border-collapse:collapse;width:100%;font-family:Arial,sans-serif'>"
            "<tr><th style='text-align:left;padding:8px'>Deal</th>"
            "<th style='text-align:left;padding:8px'>Store</th>"
            "<th style='text-align:left;padding:8px'>Price</th></tr>"
            f"{rows}</table>"
        )
    else:
        deals_html = "<p>No new deals were collected this week.</p>"

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
      <h2>Your Weekly Tech Deals Digest</h2>
      {deals_html}
      <hr style="margin:24px 0;border:none;border-top:1px solid #ddd">
      <p><strong>What specific tech deals are you looking for?</strong></p>
      <div style="border:1px solid #999;border-radius:4px;padding:10px 12px;color:#888;background:#f5f5f5;max-width:400px">
        Type your answer, then hit reply and send &rarr;
      </div>
      <p style="font-size:12px;color:#888;margin-top:16px">
        Reply to this email with what you're after (e.g. "gaming laptop" or "mechanical keyboard")
        and fresh deals matching your request will be scraped and sent back to you.
      </p>
    </div>
    """


def _build_digest_plain(deals):
    if deals:
        body = "\n".join(f"- {d['title']} ({d['place']}) - {d['price']}" for d in deals)
    else:
        body = "No new deals were collected this week."
    return (
        "Your Weekly Tech Deals Digest\n\n"
        f"{body}\n\n"
        "What specific tech deals are you looking for?\n"
        "Reply to this email with what you're after (e.g. \"gaming laptop\") "
        "and fresh deals matching your request will be scraped and sent back to you.\n"
    )


async def send_weekly_digest():
    data = _load_data()
    deals = data.get("dealsLog", [])
    _send_email(DIGEST_SUBJECT, _build_digest_plain(deals), _build_digest_html(deals))
    data["dealsLog"] = []
    data["lastWeeklyEmailSent"] = datetime.utcnow().isoformat()
    _save_data(data)


async def maybe_send_weekly_digest():
    data = _load_data()
    last_sent = data.get("lastWeeklyEmailSent")
    if last_sent and datetime.utcnow() - datetime.fromisoformat(last_sent) < WEEKLY_INTERVAL:
        return
    await send_weekly_digest()


def _extract_reply_text(body):
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            break
        if re.match(r"^On .+wrote:$", stripped):
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                return part.get_payload(decode=True).decode(errors="ignore")
        return ""
    return msg.get_payload(decode=True).decode(errors="ignore")


def scrape_amazon(query, max_results=5):
    url = f"https://www.amazon.com/s?k={requests.utils.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, "lxml")
    results = []
    for item in soup.find_all("div", attrs={"data-component-type": "s-search-result"})[:max_results]:
        title_el = item.select_one("h2 a.a-link-normal.a-text-normal")
        if not title_el:
            continue
        price_el = item.select_one("span.a-price:nth-of-type(1) span.a-offscreen")
        results.append({
            "title": title_el.get_text(strip=True),
            "url": "https://www.amazon.com" + title_el.get("href", ""),
            "price": price_el.get_text(strip=True) if price_el else "N/A",
        })
    return results


def _build_results_html(query, results):
    if results:
        body = "<ul>" + "".join(
            f"<li><a href='{r['url']}'>{r['title']}</a> - {r['price']}</li>" for r in results
        ) + "</ul>"
    else:
        body = "<p>No matching deals were found. Try a different search term.</p>"
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
      <h2>Tech Deals for: {query}</h2>
      {body}
    </div>
    """


def _build_results_plain(query, results):
    if results:
        body = "\n".join(f"- {r['title']} - {r['price']} - {r['url']}" for r in results)
    else:
        body = "No matching deals were found. Try a different search term."
    return f"Tech Deals for: {query}\n\n{body}\n"


async def check_email_replies_and_scrape(bot=None, channel_id=None):
    data = _load_data()
    last_uid = data.get("lastProcessedEmailUID", 0)

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
    imap.select("INBOX")

    status, uid_data = imap.uid("search", None, f'(HEADER SUBJECT "{DIGEST_SUBJECT}")')
    if status != "OK":
        imap.logout()
        return

    for uid_bytes in uid_data[0].split():
        uid = int(uid_bytes)
        if uid <= last_uid:
            continue

        status, msg_data = imap.uid("fetch", uid_bytes, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            last_uid = max(last_uid, uid)
            continue

        msg = email_lib.message_from_bytes(msg_data[0][1])
        from_addr = parseaddr(msg.get("From", ""))[1]
        last_uid = max(last_uid, uid)
        if from_addr.lower() != RECIPIENT_EMAIL.lower():
            continue

        query = _extract_reply_text(_get_email_body(msg))
        if not query:
            continue

        results = scrape_amazon(query)
        _send_email(
            f"Tech Deals for: {query}",
            _build_results_plain(query, results),
            _build_results_html(query, results),
        )

        if bot is not None and channel_id is not None:
            channel = bot.get_channel(channel_id)
            if channel is not None:
                from discord import Embed

                for r in results:
                    embed = Embed(
                        title=r["title"],
                        description=f'requested via email reply: "{query}" [view more]({r["url"]})',
                        timestamp=datetime.utcnow(),
                        color=0x5865F2,
                    )
                    embed.add_field(name="price", value=r["price"])
                    await channel.send(embed=embed)

    data["lastProcessedEmailUID"] = last_uid
    _save_data(data)
    imap.logout()
