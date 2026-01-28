#!/bin/bash
#
# Install script for bin-reminder
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.binreminder.daily.plist"
PLIST_SRC="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Bin Reminder - Installation"
echo "==========================="
echo

# Create logs directory
echo "Creating logs directory..."
mkdir -p "$SCRIPT_DIR/logs"

# Make script executable
echo "Making script executable..."
chmod +x "$SCRIPT_DIR/bin_reminder.py"

# Unload existing job if present
if launchctl list | grep -q "com.binreminder.daily"; then
    echo "Unloading existing job..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Copy plist to LaunchAgents
echo "Installing launchd job..."
cp "$PLIST_SRC" "$PLIST_DEST"

# Load the job
echo "Loading launchd job..."
launchctl load "$PLIST_DEST"

echo
echo "Installation complete!"
echo
echo "The script will run daily at 7:00 PM."
echo "Reminders are only sent if there's a collection the next day."
echo
echo "To test the script now, run:"
echo "  python3 $SCRIPT_DIR/bin_reminder.py"
echo
echo "To check if the job is loaded:"
echo "  launchctl list | grep binreminder"
echo
