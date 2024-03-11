#!/bin/bash

ADB_RUNNER=${ADB_RUNNER:-adb}
DEVICE_ID=${DEVICE_ID:-$($ADB_RUNNER devices | grep -v List | cut -f 1 | head -n 1)}
LOGFILE_ROOT=${LOGFILE_ROOT:-"/data/local/tmp/"}
NOW=$(date +"%Y%m%d%H%M%S")

# This script is used to get logcat from android device
echo "Running logcat on device, persisting to $LOGFILE_ROOT/logcat_$NOW.txt"
$ADB_RUNNER -s $DEVICE_ID logcat -f $LOGFILE_ROOT/logcat_$NOW.txt -d -v raw "TVM_RUNTIME:I" "*:S"

echo "Getting log file from device"
$ADB_RUNNER -s $DEVICE_ID pull $LOGFILE_ROOT/logcat_$NOW.txt ./logcat_$NOW.txt

echo "Filtering lines"
grep "Report" -A1 logcat_$NOW.txt > logcat_$NOW.txt_
rm logcat_$NOW.txt
mv logcat_$NOW.txt_ logcat_$NOW.txt

echo "Removing log file from device"
$ADB_RUNNER -s $DEVICE_ID shell rm $LOGFILE_ROOT/logcat_$NOW.txt