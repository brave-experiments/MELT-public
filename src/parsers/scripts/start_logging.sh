#!/bin/bash

# Note:   Script to clear previous logs and start logging on Android device.
# Author: Stefanos Laskaridis


ADB_RUNNER=${ADB_RUNNER:-adb}
OUTFILE_ROOT=${OUTFILE_ROOT:-"logs/"}
NOW=$(date +"%Y%m%d%H%M%S")
OUTFILE=${OUTFILE:-"logcat_${NOW}.txt"}

echo "Clearing logcat"
$ADB_RUNNER logcat -c
echo "Launching logcat persisting to file: /data/local/tmp/logcat_$NOW.txt"
$ADB_RUNNER logcat -f /data/local/tmp/logcat_$NOW.txt -v raw "TVM_RUNTIME:I" "*:S"