# MELT: Mobile Evaluation of Language Transformers

This is the catch-all repository for the codebase of our on-device evaluation of LLMs.

## Components

### Structure

```bash
├── README.md
├── batterylab/  # PhoneLab infrastructure for automated evaluation
├── frameworks/  # LLM frameworks supported by MELT
├── jetsonlab/   # JetsonLab infrastructure for
├── melt_models/ # HF models
├── melt_models_converted/ # Converted/quantized models for each backend
└── src/          # Custom code for model conversion, prompt analysis, model evaluation, and result parsing.
    ├── configs/  # Configuration per model
    ├── model_evaluation/ # Code for the model evaluation on datasets
    ├── models/   # Model conversion logic
    ├── parsers/  # Results parsing logic
    └── prompts/  # Prompt analysis logic
```

### Organisation

The codebase is structured with git submodules, for maintaining some level of separation.
For checking everything out, please run:

```bash
git submodule update --init --recursive
```

This command will checkout the latest working version for each component, recursively.

### How to run

The general workflow for running experiment goes as follows:

1. Go to `frameworks/MLC/mlc-llm` or `frameworks/llama.cpp/llama.cpp` and compile each framework. Please see the documentation ([#1](frameworks/llama.cpp/llama.cpp/build_scripts/README.md),[#2](frameworks/MLC/mlc-llm/build_scripts/README.md)) for more.
2. Go to `src/models` and download, convert models. Please see [this](src/models/README.md) for more.
3. After you build the models, you need to build the apps, that are going to be installed to the phones. To do so, please follow the rest of the documentation in ([#1](frameworks/llama.cpp/llama.cpp/build_scripts/README.md),[#2](frameworks/MLC/mlc-llm/build_scripts/README.md)).
4. Go to `batterylab/experiments/` and follow the [documentation](batterylab/experiments/README.md) there. You need to install the applications, transfer models on the local directories and then run the automated scripts.
5. If the experiment has successfully run, you'll have `batterylab/experiment_outputs/` directory populated. You can run the `batterylab/experiments/notebooks` for analysis of the results.

For running on jetson platform, you need to build each framework with the appropriate script (see ([#1](frameworks/llama.cpp/llama.cpp/build_scripts/README.md),[#2](frameworks/MLC/mlc-llm/build_scripts/README.md)). See also this [documentation](jetsonlab/README.md) for more.

### Further documentation

Additional documentation on how to run is provided in each of the subdirectories, as separate README files.

* PhoneLab [README](batterylab/experiments/README.md)
* JetsonLab [README](jetsonlab/README.md)
* llama.cpp:
    * building [README](frameworks/llama.cpp/llama.cpp/build_scripts/README.md)
    * running [README](frameworks/llama.cpp/llama.cpp/run_scripts/README.md)
* MLC-LLM:
    * building [README](frameworks/MLC/mlc-llm/build_scripts/README.md)
    * running [README](frameworks/MLC/mlc-llm/run_scripts/README.md)
* LLMFarm [README](frameworks/llama.cpp/LLMFarmEval/README.md)

## Supported frameworks

* MLC-LLM [submodule](https://github.com/brave-experiments/mlc-llm), [upstream repo](https://github.com/mlc-ai/mlc-llm)
    * TVM-Unity [submodule](https://github.com/brave-experiments/mlc-llm), [upstream repo](https://github.com/mlc-ai/relax.git)
* llama.cpp [submodule](https://github.com/brave-experiments/llama.cpp), [upstream](https://github.com/ggerganov/llama.cpp)
    * LLMFarm [submodule](https://github.com/brave-experiments/llmfarmeval), [upstream](https://github.com/guinmoon/LLMFarm)

## Supported infrastructure backends

* [JetsonLab](https://github.com/brave-experiments/jetsonlab)
* [PhoneLab](https://github.com/brave-experiments/batterylab)

## Authors/Maintainers

* Stefanos Laskaridis ([@stevelaskaridis](https://github.com/stevelaskaridis))
* Kleomenis Katevas ([@minoskt](https://github.com/minoskt))
* Lorenzo Minto ([@LorenzoMinto](https://github.com/LorenzoMinto))

## Citation

If you found this repo useful, please cite our paper "MELTing point: Mobile Evaluation of Language Transformers"

```
@article{laskaridis2024melting,
  title={MELTing point: Mobile Evaluation of Language Transformers},
  author={Laskaridis, Stefanos and Katevas, Kleomenis and Minto, Lorenzo and Haddadi, Hamed},
  journal={arXiv preprint arXiv:2403.12844},
  year={2024}
}
```