# Model automation

With these scripts, we are able to automate the download and conversion of various models.

* `download.py`: Is responsible for downloading models from Huggingface Hub.
* `convert.py`: Is responsible for converting downloaded models into the format needed per backend framework, and quantizing it to the requested bidwidth.

**Caveat**: In later versions of MLC-LLM, the conversion script is not the recommended way of converting models to MLC format (indicated in issues).
If running the latest version, please use the `convert_mlc_new.sh` script instead.


# How to run?

Before you run the downloader, it might be necessary that you define your HF API token so that you are able to download the weights (e.g. Llama-2).
Also, remember to install python requirements:

```bash
pip install -r requirements.txt
```

## Shortcut scripts

```bash
scripts/
├── convert_legacy.sh  # Convert models based on convert.py
├── convert_new.sh  # Convert models (based on MLC's new conversion scripts)
├── download_all_models.sh  # Download models from HF
└── replace_link_with_model.sh  # Util script to resolve links and copy in place
```

### Legacy vs. new

In our experiments, we had to deal with an evolving codebase. For this reason, we have tagged two version in the MLC codebase, `before_gemma` and `after_gemma`.
Conversion works as follows:

| Version      | Conversion script |
| ---          | ---               |
| before_gemma | convert_legacy.sh |
| after_gemma  | convert_new.sh    |

Before you run the conversion script, you need to define the `MLC_HOME` or `LLAMA_CPP_HOME` env vars depending on the backend specified.

## Conversion scripts

```bash
python download.py --help
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

```bash
python convert.py --help
usage: convert.py [-h] -m MODEL -d OUTPUT_DIR -b {mlc,ggml,awq} -q QUANTIZATION_MODE [-t {android,iphone,metal,cuda}] [-c CONFIG] [--only-config] [--ignore-eos] [-v]

options:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        Model name to download (should be in hf format.)
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to download the model to.
  -b {mlc,ggml,awq}, --backend {mlc,ggml,awq}
                        Backend to convert to.
  -q QUANTIZATION_MODE, --quantization-mode QUANTIZATION_MODE
                        Quantization mode to use.
  -t {android,iphone,metal,cuda}, --target {android,iphone,metal,cuda}
                        Target to compile for.
  -c CONFIG, --config CONFIG
                        Path to config file.
  --only-config         Produce only the config file
  --ignore-eos          Ignore EOS token (changes model config).
  -v, --verbose
```