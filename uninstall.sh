#!/bin/bash
#
# Uninstall script for bin-reminder
#

PLIST_NAME="com.binreminder.daily.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Bin Reminder - Uninstall"
echo "========================"
echo

if launchctl list | grep -q "com.binreminder.daily"; then
    echo "Unloading launchd job..."
    launchctl unload "$PLIST_DEST"
fi

if [ -f "$PLIST_DEST" ]; then
    echo "Removing plist..."
    rm "$PLIST_DEST"
fi

echo
echo "Uninstalled. The bin-reminder folder remains - delete it manually if desired."
echo
