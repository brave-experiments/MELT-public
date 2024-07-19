#!/bin/bash

# Note:   Script to acquire MLC logs from Android device.
# Author: Stefanos Laskaridis (stefanos@brave.com)


ADB_RUNNER=${ADB_RUNNER:-adb}
DEVICE_ID=${DEVICE_ID:-$($ADB_RUNNER devices | grep -v List | cut -f 1 | head -n 1)}
LOGFILE_ROOT=${LOGFILE_ROOT:-"/data/local/tmp/"}
OUTFILE_ROOT=${OUTFILE_ROOT:-"logs/"}
NOW=$(date +"%Y%m%d%H%M%S")
OUTFILE=${OUTFILE:-"logcat_${NOW}.txt"}

# This script is used to get logcat from android device
echo "Running logcat on device, persisting to $LOGFILE_ROOT/logcat_$NOW.txt"
$ADB_RUNNER -s $DEVICE_ID logcat -f ${LOGFILE_ROOT}/logcat_$NOW.txt -d -v raw "TVM_RUNTIME:I" "*:S"

echo "Getting log file from device"
$ADB_RUNNER -s $DEVICE_ID pull $LOGFILE_ROOT/logcat_$NOW.txt $OUTFILE

echo "Filtering lines"
grep "Report" -A1 $OUTFILE > ${OUTFILE}_
rm ${OUTFILE}
mv ${OUTFILE}_ ${OUTFILE}

echo "Removing log file from device"
$ADB_RUNNER -s $DEVICE_ID shell rm ${LOGFILE_ROOT}/logcat_$NOW.txt