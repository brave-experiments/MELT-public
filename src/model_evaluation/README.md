# MELT Model Evaluation

This directory includes the accuracy vs. model size plots for various quantisation methods in the paper.

Specifically, we support:

* HF models
* GPTQ-quantised models
* AWQ-quantised models
* llama.cpp-quantised models (k-quants)

## Structure

```bash
├── results  # includes the plotting logic for what was used in the paper
└── src  # includes the code to run evaluations on models
```

## How to run

```bash
pushd src
# Install python requirements
conda create python=3.9 -n melt_evaluations
pip install -r eval_requirements.txt
pip install git+https://github.com/PanQiWei/AutoGPTQ@d2662b18bb91e1864b29e4e05862712382b8a076

# Download models
./download_gptq_awq_models.sh

# Run evaluations
./evaluate_awq.sh
./evaluate_gptq.sh
./evaluate_hf.sh       # Needs access to models, as downloaded from (../../models)
./evaluate_llamacpp.sh # Needs separate compilation of llama.cpp and downloading of models (see ../../models)
popd
```