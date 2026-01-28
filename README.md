# Bin Reminder

Automated bin collection reminders for Bath & North East Somerset (BANES) Council. Sends a reminder the evening before your collection day via macOS Reminders and email.

## Features

- Fetches real collection dates from BANES Council API
- Handles bank holiday schedule changes automatically
- macOS Reminder + email notifications
- Runs daily at 7pm, only notifies when collection is tomorrow

## Requirements

- macOS
- Python 3
- Gmail account with App Password

## Setup

### 1. Find your UPRN

Look up your property at [uprn.uk](https://uprn.uk) using your postcode.

### 2. Create Gmail App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Create a password for "Mail" on "Mac"
3. Copy the 16-character password

### 3. Configure

```bash
cp config.example.py config.py
```

Edit `config.py` with your details:

```python
UPRN = "your_uprn_here"
EMAIL_TO = ["you@gmail.com"]  # Can be multiple addresses
EMAIL_FROM = "you@gmail.com"
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
```

### 4. Install

```bash
./install.sh
```

This installs a launchd job that runs daily at 7pm.

## Test

```bash
python3 bin_reminder.py
```

## Uninstall

```bash
./uninstall.sh
```

## Adapting for Other Councils

The BANES API endpoint is in `bin_reminder.py`. For other UK councils, check [UKBinCollectionData](https://github.com/robbrad/UKBinCollectionData) for API details.
