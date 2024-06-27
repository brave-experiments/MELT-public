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

### Further documentation

Additional documentation on how to run is provided in each of the subdirectories, as separate README files.

## Supported frameworks

* MLC-LLM [submodule](https://github.com/brave-experiments/mlc-llm), [upstream repo](https://github.com/mlc-ai/mlc-llm)
    * TVM-Unity [submodule](https://github.com/brave-experiments/mlc-llm), [upstream repo](https://github.com/mlc-ai/relax.git)
* llama.cpp [submodule](https://github.com/brave-experiments/llama.cpp), [upstream](https://github.com/ggerganov/llama.cpp)
    * LLMFarm [submodule](https://github.com/brave-experiments/llmfarmeval), [upstream](https://github.com/guinmoon/LLMFarm)

## Supported infrastructure backends

* [JetsonLab](https://github.com/brave-experiments/jetsonlab)
* [PhoneLab](https://github.com/brave-experiments/batterylab)

## Authors/Maintainers

* Stefanos Laskaridis (@stevelaskaridis)
* Kleomenis Katevas (@minoskt)
* Lorenzo Minto (@LorenzoMinto)

## Citation

If you found this repo useful, please cite our paper "MELTing point: Mobile Evaluation of Language Transformers"

```
@article{laskaridis2024melting,
  title={MELTing point: Mobile Evaluation of Language Transformers},
  author={Laskaridis, Stefanos and Kateveas, Kleomenis and Minto, Lorenzo and Haddadi, Hamed},
  journal={arXiv preprint arXiv:2403.12844},
  year={2024}
}
```