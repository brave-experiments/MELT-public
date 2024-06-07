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
