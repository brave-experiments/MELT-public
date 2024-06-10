# Per op output parser

This is a parser for the JSONs output when profiling per op. It supports MLC and llama.cpp.
In order to generate the parsable lines, the user needs to have build the respective custom backends with the appropriate flag (`BENCHMARK_PER_LAYER=1`).

* For llama.cpp, we support parsing from the logs of the CLI logs (applicable on Android and Jetsons).
* For MLC, we support parsing from the CLI and logcat logs.

## How to run

### For local logs

```bash
python parser.py -i test_files/dummy_file.mlc.log [-o CSVs] [--merge <per_op|per_module>] -b mlc
python parser.py -i test_files/dummy_file.llama_cpp.log [-o CSVs] [--merge <per_op|per_module>] -b llama.cpp
```

### For Android residing logs

```bash
cd scripts/
[ADB_RUNNER=<path_to_adb> DEVICE_ID=<android_device_id> LOGFILE_ROOT=<path_to_save_locally_on_device>] ./logcat_getter.sh
```
