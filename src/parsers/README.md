# Per op output parser

This is a parser for the JSONs output when profiling with TVM.

## How to run

### For local logs

```
python parser.py --mode file -i test_files/dummy_file.mlc.log [-o CSVs] [--merge <per_op|per_module>] -b mlc
python parser.py --mode file -i test_files/dummy_file.llama_cpp.log [-o CSVs] [--merge <per_op|per_module>] -b llama.cpp
```

### For Android residing logs

```
[ADB_RUNNER=<path_to_adb> DEVICE_ID=<android_device_id> LOGFILE_ROOT=<path_to_save_locally_on_device>] ./logcat_getter.sh
```