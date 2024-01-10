# Model Evaluation

To evaluate quantised models, we are leveraging the power of [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness).
We provide scripts for evaluating models in the following formats:
* [x] [llama.cpp](https://github.com/ggerganov/llama.cpp) quantised models
* [ ] [mlc](https://github.com/mlc-ai/mlc-llm) quantised models
* [x] [autogptq](https://github.com/PanQiWei/AutoGPTQ) quantised models
* [x] [autoawq](https://github.com/casper-hansen/AutoAWQ) quantised models

## How to run

1. Download the models:

```bash
./download_gptq_awq_models.sh
```

2. Install requirements:

```bash
git clone https://github.com/EleutherAI/lm-evaluation-harness
pushd lm-evaluation-harness
pip install -e .[gptq]
popd
pip install -r eval_requirements.txt
```

3. Run evaluations

```bash
./evaluate_gptq.sh
./evaluate_awq.sh
```