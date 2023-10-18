# Per op output parser

This is a parser for the JSONs output when profiling with TVM.

## How to run

```
python parser.py --mode file -i tests/dummy_file.log [-o CSVs] [--merge <per_op|per_module>]
```

```
[ADB_RUNNER=<path_to_adb> DEVICE_ID=<android_device_id> LOGFILE_ROOT=<path_to_save_locally_on_device>] ./logcat_getter.sh
```