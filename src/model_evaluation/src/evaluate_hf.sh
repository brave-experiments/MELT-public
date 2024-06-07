#!/bin/bash

# Note:   Script to evaluate the performance of the HF models with lm-eval suite.
# Author: Stefanos Laskaridis

MODELS=(
    TinyLlama_TinyLlama-1.1B-Chat-v0.5
    stabilityai_stablelm-zephyr-3b
    mistralai_Mistral-7B-Instruct-v0.1
    meta-llama_Llama-2-7b-hf
    meta-llama_Llama-2-13b-hf
    google_gemma-2b
    google_gemma-7b
)
TASKS=(winogrande arc_easy arc_challenge truthfulqa hellaswag)


for MODEL in ${MODELS[@]}; do
    for TASK in ${TASKS[@]}; do
        echo "Evaluating $MODEL on task $TASK"
        (lm_eval --model hf --model_args pretrained=$MODEL --tasks $TASK --batch_size auto |& tee eval_${MODEL}_${TASK}.log) &
    done
done
~