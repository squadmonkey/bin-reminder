#!/usr/bin/env python3
"""
Bin Reminder - Fetches BANES bin collection data and sends reminders.
"""

import json
import ssl
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request

# =============================================================================
# CONFIGURATION - Import from config.py (not committed to git)
# =============================================================================

from config import UPRN, EMAIL_TO, EMAIL_FROM, GMAIL_APP_PASSWORD

# =============================================================================
# API FUNCTIONS
# =============================================================================

def fetch_bin_data(uprn: str) -> dict:
    """Fetch bin collection data from BANES API."""
    url = f"https://www.bathnes.gov.uk/webapi/api/BinsAPI/v2/getbartecroute/{uprn}/true"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    # Create SSL context - use unverified for this public API
    # (macOS Python often has certificate issues)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request, context=ctx) as response:
        data = json.loads(response.read().decode())

    return data


def parse_bin_data(data: dict) -> list:
    """Parse API response into list of upcoming collections."""
    collections = []

    bin_types = {
        "residualNextDate": "Black Rubbish Bin",
        "recyclingNextDate": "Recycling (green box, food waste, cardboard)",
        "organicNextDate": "Garden Waste (green bin)",
    }

    for key, name in bin_types.items():
        if data.get(key):
            date_str = data[key]
            # Parse ISO format: 2026-01-29T00:00:00
            collection_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            collections.append({
                "type": name,
                "date": collection_date,
            })

    # Sort by date
    collections.sort(key=lambda x: x["date"])
    return collections


def get_tomorrows_collections(collections: list) -> list:
    """Filter collections that are happening tomorrow (Thursday)."""
    tomorrow = datetime.now().date() + timedelta(days=1)
    return [c for c in collections if c["date"].date() == tomorrow]

# =============================================================================
# REMINDER FUNCTIONS
# =============================================================================

def create_macos_reminder(title: str, notes: str) -> bool:
    """Create a reminder in macOS Reminders app using AppleScript."""
    # Escape quotes for AppleScript
    title_escaped = title.replace('"', '\\"')
    notes_escaped = notes.replace('"', '\\"')

    applescript = f'''
    tell application "Reminders"
        set mylist to list "Reminders"
        tell mylist
            make new reminder with properties {{name:"{title_escaped}", body:"{notes_escaped}"}}
        end tell
    end tell
    '''

    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            check=True,
            capture_output=True,
        )
        print("Created macOS Reminder")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create reminder: {e.stderr.decode()}")
        return False


def send_email(subject: str, body: str) -> bool:
    """Send email via Gmail SMTP."""
    if not GMAIL_APP_PASSWORD:
        print("Gmail App Password not configured - skipping email")
        return False

    # Handle single email or list of emails
    recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# =============================================================================
# MAIN
# =============================================================================

def main():
    print(f"Bin Reminder - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)

    # Fetch data
    print("Fetching bin collection data...")
    try:
        raw_data = fetch_bin_data(UPRN)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return 1

    # Parse collections
    collections = parse_bin_data(raw_data)

    # Get tomorrow's collections
    tomorrows = get_tomorrows_collections(collections)

    if not tomorrows:
        print("No collections tomorrow - nothing to remind about")
        # Still show upcoming collections for info
        print("\nUpcoming collections:")
        for c in collections[:3]:
            print(f"  - {c['type']}: {c['date'].strftime('%A %d %B')}")
        return 0

    # Build reminder message
    bin_list = "\n".join([f"  - {c['type']}" for c in tomorrows])
    tomorrow_date = tomorrows[0]["date"].strftime("%A %d %B")

    reminder_title = f"Put bins out tonight!"
    reminder_body = f"Collection tomorrow ({tomorrow_date}):\n{bin_list}"

    print(f"\n{reminder_title}")
    print(reminder_body)
    print()

    # Create macOS reminder
    create_macos_reminder(reminder_title, reminder_body)

    # Send email
    email_subject = f"Bin Reminder: Collection tomorrow ({tomorrow_date})"
    email_body = f"""Hi,

This is your weekly bin reminder.

{reminder_body}

Remember to put them out tonight!

---
Automated reminder from bin-reminder
"""
    send_email(email_subject, email_body)

    return 0


if __name__ == "__main__":
    exit(main())
