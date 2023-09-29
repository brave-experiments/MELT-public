# Model automation

With these scripts, we are able to automate the download and conversion of various models.

* `download.py`: Is responsible for downloading models from Huggingface Hub.
* `convert.py`: Is responsible for converting downloaded models into the format needed per backend framework, and quantizing it to the requested bidwidth.

# How to run?

Before you run the downloader, it might be necessary that you define your HF API token so that you are able to download the weights (e.g. Llama-2).

```
usage: download.py [-h] -m MODELS [MODELS ...] -d DOWNLOAD_DIR [-f] [-t TOKEN]

options:
  -h, --help            show this help message and exit
  -m MODELS [MODELS ...], --models MODELS [MODELS ...]
                        Model name to download (should be in hf format.)
  -d DOWNLOAD_DIR, --download-dir DOWNLOAD_DIR
                        Directory to download the model to.
  -f, --force           Overwrite existing files.
  -t TOKEN, --token TOKEN
```

Before you run the conversion script, you need to define the `MLC_HOME` or `LLAMA_CPP_HOME` env vars depending on the backend specified.

```
python convert.py --help
usage: convert.py [-h] -m MODELS [MODELS ...] -d OUTPUT_DIR -b {mlc,ggml} -q QUANTIZATION_MODE [-t {android,ios,metal}] --max-seq-length MAX_SEQ_LENGTH [-v]

options:
  -h, --help            show this help message and exit
  -m MODELS [MODELS ...], --models MODELS [MODELS ...]
                        Model name to download (should be in hf format.)
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to download the model to.
  -b {mlc,ggml}, --backend {mlc,ggml}
                        Backend to convert to.
  -q QUANTIZATION_MODE, --quantization-mode QUANTIZATION_MODE
  -t {android,ios,metal}, --target {android,ios,metal}
  --max-seq-length MAX_SEQ_LENGTH
  -v, --verbose
```
